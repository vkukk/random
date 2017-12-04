import requests
import sys
import json
import argparse
from bs4 import BeautifulSoup

"""
parameetrid = ['name', 'description', 'sku', 'keel', 'autor', 'kirjastus', 'sari']
"""

# Script arguments
parser = argparse.ArgumentParser(description='Selle skriptiga saab Apollo veebipoest raamatute andmeid pärida.')
# config file is always required
parser.add_argument('--nimi', help='Anna raamatu nimi.', required=True)
args = parser.parse_args()
parsed_name = args.nimi.replace(' ', '+')


def main():
    # Compile url from argument and static part
    try:
        query_url = 'https://www.apollo.ee/catalogsearch/advanced/result/?name=' + str(parsed_name) + '&kategooria[]=181'
        # print(query_url)
    except Exception as e:
        print(e)
        sys.exit(1)
    # Get page
    try:
        page = requests.get(query_url, 10.0)
    except Exception as e:
        print(e)
        sys.exit(1)
    # Parse with BeautifulSoup
    soup = BeautifulSoup(page.text, 'html.parser')
    # Get product page url from search result page by CSS class
    product_name_url = soup.find(class_='product-image')
    # only href content tag (user later by requests))
    product_url = product_name_url.get('href')
    # Run data extraction function
    extract_product_data(product_url)


def extract_product_data(p_url):
    p_data_dict = {}
    try:
        product_page = requests.get(p_url)
    except Exception as e:
        print(e)
        sys.exit(1)
    # Parse page
    ps = BeautifulSoup(product_page.text, 'html.parser')
    # Product name is in h1 tag
    p_name = ps.find("h1")
    p_data_dict['Nimi'] = p_name.text
    # Get product attribute table
    psa = ps.find(id='product-attribute-specs-table')
    # List of <li> elements that contain needed data
    psa_li = psa.find_all("li")
    # Iterate over product data
    for li in psa_li:
        # Strip and split
        li_content = li.text.strip().split(':')
        # Need to strip again before putting into dictionary
        p_data_dict[li_content[0].strip()] = li_content[1].strip()
    # Return result in visually pleasing form, use UTF
    print(json.dumps(p_data_dict, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()

