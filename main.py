
import scan_functs
import product_functs
#import SQL_functs
import sqlite3
import datetime
import pandas as pd


#Settings
msg = 1 #Flag for displaying more info 1 or 0

# Connect to database
conn = sqlite3.connect('database.db')
curs = conn.cursor()

#curs.execute("DELETE FROM stock2 WHERE ean = 5000119014436")
#curs.execute("ALTER TABLE stock2 ADD COLUMN identifier INTEGER")


# Execute an SQL query on the SQLite database and return results as a dataframe
def sql_to_dataframe(query, pars=0):
    if pars:
        df = pd.read_sql(query, conn, params=pars)
    else:
        df = pd.read_sql(query, conn)
    return df

# Use barcode scan info to search API for product information
def get_product_from_scan():
    got_prod = 0  # Flag to determine when we were successful with a scan

    while got_prod == 0:
        print("Please scan")
        # prd_ean = scan_functs.return_scan_value()
        prd_ean = 5000119014436
        print(prd_ean)
        # Below three lines for testing only
        # prd_desc = 'Test prod'
        # print(prd_desc + ' scanned')
        # got_prod = 1

        # Get product info
        prd_info = product_functs.searchEAN(prd_ean, msg)

        prd_desc = prd_info["products"][0]["description"]
        print(prd_desc + ' scanned')
        got_prod = 1

        return prd_ean, prd_desc

# See if there is already stock for this product
def check_db_for_product(ean, sdate=0):
    if sdate == 0:
        a = curs.execute("SELECT SUM(qty) FROM stock2 WHERE ean = ? AND end_date IS NULL", (ean,))
    else:
        a = curs.execute("SELECT SUM(qty) FROM stock2 WHERE ean = ? AND entry_date = ? AND end_date IS NULL", (ean,sdate))

    exist_qty = None
    for row in a:
        if row[0]:
            exist_qty = int(row[0])
    return exist_qty

def add_to_database(prd_ean, prd_desc, nowdate):
    # First check if we're about to create a duplicate row
    same_item_today = check_db_for_product(prd_ean, nowdate)

    if same_item_today is None:
        # Insert new row for this product into database with today as startdate and entry date, identifier 1
        insert_data = (prd_ean, prd_desc, nowdate, 1, nowdate)
        curs.execute("INSERT INTO stock2 VALUES(?,?,?,null,?,?,null,1)", insert_data)
        print('Added to list')
    else:
        # Insert new row for this product into database with today as startdate and entry date
        insert_data = (prd_ean, prd_desc, nowdate, 1, nowdate, same_item_today+1)
        curs.execute("INSERT INTO stock2 VALUES(?,?,?,null,?,?,null,?)", insert_data)
        print('Added to list')

def remove_from_database(prd_ean, prd_desc, nowdate):
    # Act on row with earliest entry_date...
    a = curs.execute("SELECT MIN(entry_date) FROM stock2 WHERE ean = ? AND end_date IS NULL", (prd_ean,))
    for row in a:
        earliest_date = row[0]
    # ...and largest identifier
    a = curs.execute("SELECT MAX(identifier) FROM stock2 WHERE ean = ? AND entry_date = ? AND end_date IS NULL", (prd_ean, earliest_date))
    for row in a:
        max_identifier = row[0]

    # End date the row
    update_data = (nowdate, prd_ean, earliest_date, max_identifier)
    curs.execute("UPDATE stock2 SET end_date = ? WHERE ean = ? AND end_date IS NULL AND entry_date = ? AND identifier = ?", update_data)

def current_info(prd_ean=0):
    # If product supplied, show info for that product only
    if prd_ean:
        # Show live records for this product
        results = sql_to_dataframe("SELECT * FROM stock2 WHERE ean = :ean AND end_date IS NULL", {"ean":prd_ean})
        sentence = results[["qty", "desc"]].to_string(index=False, header=False) +  " were added on " + results['entry_date'].to_string(index=False, header=False)
        print(sentence)
    else:
        print("Cupboards now contain:")
        results = sql_to_dataframe("SELECT SUM(qty) AS qty, desc, MIN(entry_date) AS date_1st_added FROM stock2 WHERE end_date IS NULL GROUP BY 2")
        print(results[["qty", "desc", "date_1st_added"]].to_string(index=False))

# Generate a list of products that we used to have but no longer have, ordered by reverse end date
def show_shopping_list():
    # Find products that we don't have any of anymore
    all_prods = sql_to_dataframe("SELECT ean, desc, COUNT(*) AS all_recs, SUM(CASE WHEN end_date IS NOT NULL THEN 1 ELSE 0 END) AS ended_recs FROM stock2 GROUP BY 1,2")
    all_prods = all_prods[all_prods["all_recs"] == all_prods["ended_recs"]]

    if len(all_prods["ean"]) > 0:

        print("You've run out of:")
        #all_prods.sort_values("start_date", axis=0, ascending=False)
        print(all_prods["desc"].to_string())
    else:
        print("You don't need anything")

def input_from_scan():
    # Use barcode scan info to search API for product information
    prd_ean, prd_desc = get_product_from_scan()

    # Check if we already have information on this product
    exist_qty = check_db_for_product(prd_ean)

    # Get current date, to be used later
    nowdate = datetime.datetime.now().strftime("%Y-%m-%d")

    # If we don't have entries for this product we must be wanting to add the product to the database
    if exist_qty is None or exist_qty == 0:
        add_to_database(prd_ean, prd_desc, nowdate)
        print("Inserted into database")
    elif exist_qty > 0:
        # Otherwise there are multiple things we may want to do
        opt = input("Records found, would you like to Add, Remove or View? (a/r/v)")
        if opt == "A" or opt == "a":
            add_to_database(prd_ean, prd_desc, nowdate)
        if opt == "R" or opt == "r":
            remove_from_database(prd_ean, prd_desc, nowdate)
        if opt == "V" or opt == "v":
            current_info(prd_ean)

def input_text():
    # Get the text we want to search for
    txt = input("Which product are you looking for?")
    # Send a request to the grocery search API and receive a list of products
    prd_info = product_functs.product_text_search(txt, msg)
    for i in len(prd_info["products"]):
        prd_desc = prd_info["products"][i]["description"]
        print(prd_desc + ' found')


def main():

    # Ask whether we want to scan a barcode, or search for a product by text
    ans = input("Barcode or text search? (b/t)")
    if ans in ('b','B','1'):
        input_from_scan()
    else:
        input_text()

    # Show all products in the database
    current_info()

    show_shopping_list()

    if msg:
        db = sql_to_dataframe("SELECT * FROM stock2")
        print(db.to_string())

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
