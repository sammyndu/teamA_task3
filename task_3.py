
''' script for filling university locations based on dataset provided '''

import json
import requests
import pandas as pd
from iso3166 import countries
from config import api_key # saved the api key in a config file and imported it

# read data from csv
df = pd.read_csv("university-names.csv")

# place api url for getting the place id of the univeristy searched
place_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

# place details api url for getting more details on the university
# serached using the place id gotten from place api url
details_url = "https://maps.googleapis.com/maps/api/place/details/json?"

# create  a column for the locations
df["location"] = None

# loop through each row and use the university name and
# and the university country code to search for its location
for i in range(0, len(df)):
    # combine the university name and the country name gotten from the country code
    query = df.iat[i, 1]+" "+countries.get(df.iat[i, 2]).name

    # get the CCTLD which is will be needed to prioritize the country code given
    region = countries.get(df.iat[i, 2]).alpha2

    # GET request on places api
    place_response = requests.get(place_url + 'query=' \
        + query + '&key=' + api_key  + \
            '&region=' + region)

    data = place_response.json()

    # checks if places api returns zero results
    if not data['results']:
        df.iat[i, df.columns.get_loc("location")] = float('NaN')
        continue
    else:
        # obtain place id from place api response
        place_id = data['results'][0]['place_id']

        #GET request using the place id gotten from places api
        details_response = requests.get(details_url + 'place_id=' + place_id + '&key=' + api_key)
        details_data = details_response.json()

        # obtain address details from place details response
        loc = details_data['result']['address_components']
        for j in loc:
            # loop through the adrress details and find admin area level 1
            if j['types'] == ['administrative_area_level_1', 'political']:
                location = j['long_name']
            # checks the country to ensure its the same as the one given in the dataset
            if j['types'] == ['country', 'political'] and j['short_name'] != region:
                location = float('NaN')

        # input data in the location column for the current row
        df.iat[i, df.columns.get_loc("location")] = location

# send data to csv file
df.to_csv("university-names.csv", index=False)