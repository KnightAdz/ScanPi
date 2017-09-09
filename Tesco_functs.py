import json
import urllib.request
import codecs
import requests


dev_key = open('dev_key.txt').readline()
app_key = open('app_key.txt').readline()

#
#Function to grab json data from a given url
#	
def datafromurl(url):
    r = urllib.request.urlopen(url)
    reader = codecs.getreader('utf-8')
    return json.load(reader(r))
	


###
#Login and get session key
###	
def connect_to_tesco(msg):
    if msg == 1:
        print('Connecting to Tesco')

    login_url = 'https://secure.techfortesco.com/tescolabsapi/restservice.aspx?command=LOGIN&email=&password=&developerkey='+dev_key+'&applicationkey='+app_key
    login_data = datafromurl(login_url)

    if msg == 1:
        print(login_data["StatusInfo"])

    return login_data['SessionKey']


###
#Search for products by EAN
###
def return_prod_info(EAN, session_key, msg):	
    if msg == 1:
        print('Searching for product...')
        
    search_url = 'https://secure.techfortesco.com/tescolabsapi/restservice.aspx?command=PRODUCTSEARCH&EANBarcode='+EAN+'&page=1&sessionkey='+session_key
    search_data = datafromurl(search_url)
    if msg == 1:
        print(search_data["StatusInfo"])

    #print(search_data.keys())
    return search_data


def add_to_basket(Tesco_prod_id):
    # load maker key from file
    maker_key_file = open("Maker key.txt")
    maker_key = maker_key_file.readline()
    print(maker_key)

    # prepare request
    action = "product_scann"

    product_id = {}
    product_id["value1"] = Tesco_prod_id

    url_request = "https://maker.ifttt.com/trigger/" + action + "/with/key/" + maker_key

    print(url_request)
    # make request to IFTTT server
    r = requests.post(url_request, data=product_id)
    print(r)