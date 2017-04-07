import json
import urllib.request
import codecs

dev_key = 'VLR6prKN3KKse83ZWZuM'
app_key = '4945D0D89D9FB604A11A'

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
