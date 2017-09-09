import requests


def main():
    # load maker key from file
    maker_key_file = open("Maker key.txt")
    maker_key = maker_key_file.readline()
    print(maker_key)

    # prepare request
    action = "product_scann"

    product_id = {}
    product_id["value1"] = 275280804

    url_request = "https://maker.ifttt.com/trigger/" + action + "/with/key/" + maker_key

    print(url_request)
    # make request to IFTTT server
    r = requests.post(url_request, data=product_id)
    print(r)


if __name__ == "__main__":
    main()
