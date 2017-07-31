import json
import urllib.request
import codecs
import http.client, urllib.parse, urllib.error, base64


#dev_key = 'VLR6prKN3KKse83ZWZuM'
#app_key = '4945D0D89D9FB604A11A'


headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': 'a55592d63ae2410eb7cffd2d3778885b ',
}

#
#Function to grab json data from a given url
#	
def datafromurl(url):
    r = urllib.request.urlopen(url)
    reader = codecs.getreader('utf-8')
    return json.load(reader(r))

###
#Login and get session key (Old API function)
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
#Search for products by EAN (Old API function)
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


###
#Search for products by EAN (Old API function)
###
def searchEAN(EAN, msg):	
    if msg == 1:
        print('Searching for product...')
    
    # Request parameters
    params = urllib.parse.urlencode({'gtin': EAN})
    
    try:
        conn = http.client.HTTPSConnection('dev.tescolabs.com')
        conn.request("GET", "/product/?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()

    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    if msg == 1:
                print(data)

    conn.close()
    #Convert to JSON format before returning    
    jsondata = json.loads(data)      
    
    return jsondata
####################################

def product_text_search(txt, msg):

    if msg == 1:
        print('Searching for product...')

    params = urllib.parse.urlencode({'query': txt, 'offset': 0, 'limit' : 9})

    try:
        conn = http.client.HTTPSConnection('dev.tescolabs.com')
        conn.request("GET", "/grocery/products/?query={query}&offset={offset}&limit={limit}&%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    if msg == 1:
        print(data)

    jsondata = json.loads(data)

    return jsondata

####################################
