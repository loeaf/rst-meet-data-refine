import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import mysql.connector
import json

# open the JSON file
with open('config.json') as f:
    # load the contents of the file into a dictionary
    data = json.load(f)

user = data['user']
password = data['password']
host = data['host']
db = data['db']
# establish a connection to the MySQL server
cnx = mysql.connector.connect(user=user, password=password, host=host, database=db)

def getAddress(value):
    encoded_address = urllib.parse.quote_plus(value.strip())
    url = f'https://jusoga.com/search?q={encoded_address}'

    time.sleep(1)
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')

    links = soup.find_all('a')

    for a in links:
        href = a.get('href')
        time.sleep(1)
        print(href)
        # check inclue https
        if href is not None and href.startswith('https'):
            lng = ''
            lat = ''
            state = False

            response = requests.get(href)
            html_content = response.content
            div_soup = BeautifulSoup(html_content, 'html.parser')

            # Find the <tr> elements on the page that contain the latitude and longitude
            trs = div_soup.findAll('tr')
            # check size
            if len(trs) == 0:
                return None
            else:
                for tr in trs:
                    lat_tr = tr.find('th', text='위도')
                    lng_tr = tr.find('th', text='경도')
                    # Extract the latitude and longitude values from the <td> elements
                    if lat_tr:
                        lat = tr.find('td').text
                        state = True
                    if lng_tr:
                        lng = tr.find('td').text
                        state = True
                if state:
                    print(lat, lng)
                    return lat + ',' + lng

def selectByData(value):
    # create a cursor object to execute SQL queries
    cursor = cnx.cursor()
    # select query
    query = 'SELECT id, road_address FROM restaurant'
    # execute the query
    cursor.execute(query)
    # fetch all the rows returned by the query
    rows = cursor.fetchall()
    # print the rows
    for row in rows:
        print(row)
        result = getAddress(row[1])
        if result is not None:
            updateByData(result, row[0])
    # close the cursor and connection
    cursor.close()

def updateByData(value, id):
    # create a cursor object to execute SQL queries
    cursor = cnx.cursor()
    # define the SQL query
    geo = value.split(',')
    query = "UPDATE restaurant SET longitude=%s, latitude=%s WHERE id=%s"
    # execute the query
    print(query)
    cursor.execute(query, (geo[1], geo[0], id))
    # fetch all the rows ret
    rows = cursor.fetchall()
    # print the rows
    for row in rows:
        print(row)

    cnx.commit()
    # close the cursor and connection
    cursor.close()

selectByData('');

# with open('sejsong.txt', 'r', encoding='utf-8') as f:
#     lines = f.readlines()
#     for line in lines:
#         print(line)
#         getAddress(line)

cnx.close()