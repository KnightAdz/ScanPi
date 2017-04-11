
import scan_functs
import product_functs
#import SQL_functs
import sqlite3
import datetime


#Settings
msg = 1 #Flag for displaying more info 1 or 0


#Old Tesco API is defunct
#api_session_key = Tesco_functs.connect_to_tesco(msg)


got_prod = 0 #Flag to determine when we were successful with a scan


while got_prod == 0:
    print("Please scan")
    prd_ean = scan_functs.return_scan_value()
    print(prd_ean)
    #Below three lines for testing only
    #prd_desc = 'Test prod'
    #print(prd_desc + ' scanned')
    #got_prod = 1

    
    #Get product info
    prd_info = product_functs.searchEAN(prd_ean, msg)
  
    
    prd_desc = prd_info["products"][0]["description"]
    print(prd_desc + ' scanned')
    got_prod = 1




        

#Connect to database
conn = sqlite3.connect('database.db')
curs = conn.cursor()


#curs.execute("CREATE TABLE stock2 AS SELECT ean, desc, entry_date, codelife, NULL AS qty, NULL AS start_date, end_date FROM stock")


nowdate = datetime.datetime.now().strftime("%Y-%m-%d")

#See if there is already stock for this product
a = curs.execute("SELECT SUM(qty) FROM stock2 WHERE ean = ? AND end_date IS NULL",(prd_ean,))
for row in a:
    exist_qty = row[0]

if int(exist_qty) > 0:
    done = 0
    while done==0:
        opt = input("Records found, would you like to Add, Remove or View? (a/r/v)")
        if (opt == "A" or opt == "a"):
            #Action depends on whether more rows exist with this entry/start date
            a = curs.execute("SELECT SUM(qty) FROM stock2 WHERE ean = ? AND start_date = ? AND entry_date = ? AND end_date IS NULL", (prd_ean,nowdate,nowdate))
            for row in a:
                current_qty = row[0]

            if int(current_qty) > 0:
                #Update the qty
                current_qty = current_qty+1
                curs.execute("UPDATE stock2 SET qty = ? WHERE ean = ? AND start_date = ? AND entry_date = ? AND end_date IS NULL", (current_qty, prd_ean,nowdate,nowdate))
            else:
                #Insert new row for this product into database with today as startdate and entry date
                insert_data = (prd_ean, prd_desc, nowdate, 1, nowdate)
                curs.execute("INSERT INTO stock2 VALUES(?,?,?,null,?,?,null)",insert_data)
            done = 1
        if (opt == "R" or opt == "r"):
            #Act on row with earliest entry_date
            a = curs.execute("SELECT MIN(entry_date) FROM stock2 WHERE ean = ? AND end_date IS NULL", (prd_ean,))
            for row in a:
                earliest_date = row[0]
            #Get the qty on this row
            a = curs.execute("SELECT SUM(qty) FROM stock2 WHERE ean = ? AND entry_date = ? AND end_date IS NULL", (prd_ean, earliest_date))
            for row in a:
                early_qty = row[0]

            #End date the row
            update_data = (nowdate, prd_ean, earliest_date)
            curs.execute("UPDATE stock2 SET end_date = ? WHERE ean = ? AND end_date IS NULL AND entry_date = ?",update_data)
            #Add a new row with reduced qty
            insert_data = (prd_ean, prd_desc, earliest_date, early_qty-1, nowdate)
            curs.execute("INSERT INTO stock2 VALUES(?,?,?,null,?,?,null)",insert_data)
            done = 1
        if (opt == "V" or opt == "v"):
            #Show live records for this product
            for row in curs.execute("SELECT * FROM stock2 WHERE ean = ? AND end_date IS NULL", (prd_ean,)):
                print(row)
            done = 1
else:
    insert_data = (prd_ean, prd_desc, nowdate, 1, nowdate)
    a = curs.execute("INSERT INTO stock2 VALUES(?,?,?,null,?,?,null)",insert_data)
    print("Inserted into database")


print("Database now contains:")
for row in curs.execute("SELECT * FROM stock2"):
    print(row)

conn.commit()
conn.close()

