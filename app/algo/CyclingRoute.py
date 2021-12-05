import requests
import pandas as pd
import googlemaps
import os
import polyline
from dotenv import load_dotenv

""" Create a csv of latitude and longitude points for the most common google map cycling route
    between a start and end point.
    Constrcutor should be passed:
        * a lat, long string of start point, formatted as such: 
            '39.74004472948581, -105.22779556239729'
        * a lat, long string of end point, formatted as such:
            '39.73310023877332, -105.23766244168166'
"""


class CyclingRoute():

    def __init__(self, beg_coords, end_coords, mode="bicycling"):
        self.start = beg_coords
        self.end = end_coords
        self.mode = mode
        load_dotenv()
        self.API_key = os.environ.get('KEY')

    def get_elevation(lat, long):
        query = ('https://api.open-elevation.com/api/v1/lookup'
                 f'?locations={lat},{long}')
        r = requests.get(query).json()
        elevation = pd.json_normalize(r, 'results')['elevation'].values[0]
        return elevation

    def to_csv(self, filepath="gen_route.csv"):
        gmaps = googlemaps.Client(key=self.API_key)
        # Request directions
        directions_result = gmaps.directions(
            self.start, self.end, mode="bicycling")

        line = directions_result[0].get("overview_polyline").get("points")
        coords = polyline.decode(line)

        lat_long_alt = []
        for coord in coords:
            lat_long_alt.append(
                (coord[0], coord[1], CyclingRoute.get_elevation(coord[0], coord[1])))
        df = pd.DataFrame(lat_long_alt, columns=[
                          "latitude", "longitude", "altitude"])
        df["time"] = [i+1 for i in range(len(df.index))]
        df.to_csv(filepath)


""" Example run:

    lookout_start = '39.74004472948581, -105.22779556239729'
    lookout_end = '39.73310023877332, -105.23766244168166'
    route = CyclingRoute(lookout_start, lookout_end)
    route.to_csv("lookout.csv")

"""
