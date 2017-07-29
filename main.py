
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
def check_db_for_product(ean):
    a = curs.execute("SELECT SUM(qty) FROM stock2 WHERE ean = ? AND end_date IS NULL", (ean,))
    exist_qty = 0
    for row in a:
        if row[0]:
            exist_qty = int(row[0])
    return exist_qty

def add_to_database(prd_ean, prd_desc, nowdate):
    # Action depends on whether more rows exist with this entry/start date
    res = sql_to_dataframe("SELECT SUM(IFNULL(qty,0)) AS qty FROM stock2 WHERE ean = :ean AND start_date = :sdate AND entry_date = :edate AND end_date IS NULL",
                           {'ean': prd_ean, 'sdate': nowdate, 'edate': nowdate})

    if res["qty"].iloc[0]:
        current_qty = res["qty"].iloc[0]
    else:
        current_qty = 0

    if current_qty > 0:
        # Update the qty
        current_qty = current_qty + 1
        curs.execute(
            "UPDATE stock2 SET qty = ? WHERE ean = ? AND start_date = ? AND entry_date = ? AND end_date IS NULL",
            (current_qty, prd_ean, nowdate, nowdate))
    else:
        # Insert new row for this product into database with today as startdate and entry date
        insert_data = (prd_ean, prd_desc, nowdate, 1, nowdate)
        curs.execute("INSERT INTO stock2 VALUES(?,?,?,null,?,?,null)", insert_data)
    print('Added to list')

def remove_from_database(prd_ean, prd_desc, nowdate):
    # Act on row with earliest entry_date
    a = curs.execute("SELECT MIN(entry_date) FROM stock2 WHERE ean = ? AND end_date IS NULL", (prd_ean,))
    for row in a:
        earliest_date = row[0]
    # Get the qty on this row
    a = curs.execute("SELECT SUM(qty) FROM stock2 WHERE ean = ? AND entry_date = ? AND end_date IS NULL",
                     (prd_ean, earliest_date))
    for row in a:
        early_qty = row[0]

    # End date the row
    update_data = (nowdate, prd_ean, earliest_date)
    curs.execute("UPDATE stock2 SET end_date = ? WHERE ean = ? AND end_date IS NULL AND entry_date = ?", update_data)
    # Add a new row with reduced qty
    insert_data = (prd_ean, prd_desc, earliest_date, early_qty - 1, nowdate)
    curs.execute("INSERT INTO stock2 VALUES(?,?,?,null,?,?,null)", insert_data)

def current_info(prd_ean=0):
    # If product supplied, show info for that product only
    if prd_ean:
        # Show live records for this product
        results = sql_to_dataframe("SELECT * FROM stock2 WHERE ean = :ean AND end_date IS NULL", {"ean":prd_ean})
        sentence = results[["qty", "desc"]].to_string(index=False, header=False) +  " were added on " + results['entry_date'].to_string(index=False, header=False)
        print(sentence)
    else:
        print("Database now contains:")
        results = sql_to_dataframe("SELECT * FROM stock2 WHERE end_date IS NULL")
        print(results[["qty", "desc", "entry_date"]].to_string(index=False))

def main():
    # Use barcode scan info to search API for product information
    prd_ean, prd_desc = get_product_from_scan()

    # Check if we already have information on this product
    exist_qty = check_db_for_product(prd_ean)

    # Get current date, to be used later
    nowdate = datetime.datetime.now().strftime("%Y-%m-%d")

    # If we do have entries for this product
    if exist_qty > 0:
        # There are multiple things we may want to do
        opt = input("Records found, would you like to Add, Remove or View? (a/r/v)")
        if opt == "A" or opt == "a":
            add_to_database(prd_ean, prd_desc, nowdate)
        if opt == "R" or opt == "r":
            remove_from_database(prd_ean, prd_desc, nowdate)
        if opt == "V" or opt == "v":
            current_info(prd_ean)
    # If not, we must be wanting to add the product to the database
    else:
        insert_data = (prd_ean, prd_desc, nowdate, 1, nowdate)
        a = curs.execute("INSERT INTO stock2 VALUES(?,?,?,null,?,?,null)",insert_data)
        print("Inserted into database")


    current_info()

    #for row in curs.execute("SELECT * FROM stock2"):
    #    print(row[1])

    #prod_data = pd.DataFrame(curs.execute("SELECT * FROM stock2"))
    #print(prod_data)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()