
#Form the main query for entering product amounts into database
def insert_prod_data_query(ean, desc, qty, date):
    q_str = "INSERT INTO stock(?,?,?,?);",ean,desc,qty,date)
    return q_str


