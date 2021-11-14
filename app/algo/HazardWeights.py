import pandas as pd
import statistics
import geopy.distance
from numpy_ext import rolling_apply
import math
import json

""" Create a hazard profile from an input csv
        * input csv should have features time, latitude, longitude, altitude
        * headers in csv should be named: Lat,Long,altitude,time (any order)
        * running_avg_points is number of timesteps to perform rolling averages with
    Modifies passed in CSV to add a hazard weights column
"""


class HazardWeights():
    GradeMulti = [1.1, 1.2, 1.3, 1.4, 1.5, 1.5, 1.6,
                  1.6, 1.7, 1.7, 1.8, 1.8, 1.8, 1.9, 1.9, 2.0]
    CurveMulti = GradeMulti
    VelocityMulti = [1+i*.1 for i in range(1, 11)]
    AccMulti = [1.1, 1.3, 1.4, 1.6, 1.7, 1.8, 1.8, 1.9, 1.9, 2.0]

    def __init__(self, csv, running_avg_pts=3):
        self.data = pd.read_csv(csv)
        self.running_avg_points = running_avg_pts
        self.calc_hazard()

    def distance_between(lat, long):
        loc1 = (lat.iloc[0], long.iloc[0])
        loc2 = (lat.iloc[1], long.iloc[1])
        return geopy.distance.distance(loc1, loc2).miles

    def herons_formula(a, b, c):
        s = (a+b+c)/2
        if s*(s-a)*(s-b)*(s-c) < 0:
            return 0
        return math.sqrt(s*(s-a)*(s-b)*(s-c))

    def turn_radius(lat, long):
        loc1 = (lat.iloc[0], long.iloc[0])
        loc2 = (lat.iloc[1], long.iloc[1])
        loc3 = (lat.iloc[2], long.iloc[2])
        s1 = geopy.distance.distance(loc1, loc2).miles
        s2 = geopy.distance.distance(loc2, loc3).miles
        s3 = geopy.distance.distance(loc1, loc3).miles
        A = HazardWeights.herons_formula(s1, s2, s3)
        radius = 2*A/s3
        return radius

    def diff_index(a, b, limit):
        index = abs(math.floor(10*abs(a-b)/((a+b)/2)))
        if index > limit-1:
            return limit-1
        else:
            return index

    def hazard(vel, avgVel, grade, avgGrade, accl, avgAccl, turn_radius):
        VML = 1
        AML = 1
        GML = 1
        RML = 1
        if vel.iloc[0] > avgVel.iloc[0]:
            VML = HazardWeights.VelocityMulti[HazardWeights.diff_index(
                vel.iloc[0],  avgVel.iloc[0], len(HazardWeights.VelocityMulti))]
        if accl.iloc[0] > avgAccl.iloc[0]:
            AML = HazardWeights.AccMulti[HazardWeights.diff_index(
                accl.iloc[0],  avgAccl.iloc[0], len(HazardWeights.AccMulti))]
        if grade.iloc[0] > avgGrade.iloc[0]:
            GML = HazardWeights.GradeMulti[HazardWeights.diff_index(
                grade.iloc[0],  avgGrade.iloc[0], len(HazardWeights.GradeMulti))]
        if turn_radius.iloc[0] > 0:
            RML = HazardWeights.CurveMulti[HazardWeights.diff_index(
                turn_radius.iloc[0],  0, len(HazardWeights.CurveMulti))]
        return VML*AML*GML*RML

    def calc_hazard(self):
        # calculate distance between
        self.data["distance_between"] = rolling_apply(
            HazardWeights.distance_between, 2, self.data["Lat"], self.data["Long"])
        self.data.at[0, "distance_between"] = 0
        # calculating velocity, acceleration, and a running average velocity
        self.data["velocity"] = self.data["distance_between"].diff() / \
            self.data["time"].diff()
        self.data.at[0, "velocity"] = 0
        self.data["acceleration"] = self.data["velocity"].diff() / \
            self.data["time"].diff()
        self.data.at[0, "acceleration"] = 0
        self.data["runAvgVel"] = self.data["velocity"].rolling(
            self.running_avg_points).mean()
        self.data["runAvgAccel"] = self.data["acceleration"].rolling(
            self.running_avg_points).mean()
        for i in range(self.running_avg_points):
            self.data.at[i, "runAvgVel"] = statistics.mean(
                [self.data.at[j, "velocity"] for j in range(i+1)])
            self.data.at[i, "runAvgAccel"] = statistics.mean(
                [self.data.at[j, "acceleration"] for j in range(i+1)])
        # calculating grade and running average grade from altitude
        self.data["grade"] = 100 * self.data["altitude"].diff(periods=self.running_avg_points) \
            / self.data["distance_between"].diff(periods=self.running_avg_points)
        self.data.at[0:self.running_avg_points-1, "grade"] = 0
        self.data["runAvgGrade"] = self.data["grade"].rolling(
            self.running_avg_points).mean()
        for i in range(self.running_avg_points):
            self.data.at[i, "runAvgGrade"] = statistics.mean(
                [self.data.at[j, "grade"] for j in range(i+1)])
        dist_vec_len = 4
        self.data["turnRadius"] = rolling_apply(
            HazardWeights.turn_radius, 3, self.data["Lat"], self.data["Long"])
        for i in range(dist_vec_len):
            self.data.at[i, "turnRadius"] = 0
        self.data["hazard"] = rolling_apply(HazardWeights.hazard, 1, self.data["velocity"], self.data["runAvgVel"],
                                            self.data["grade"], self.data["runAvgGrade"], self.data["acceleration"],
                                            self.data["runAvgAccel"], self.data["turnRadius"])
        self.data.at[0, "hazard"] = 0

    def to_json(self, filename="weights.json", minimal=True):
        if minimal:
            with open(filename, 'w') as outfile:
                json.dump(self.data[['Lat', 'Long', 'hazard']].to_dict(
                    'records'), outfile)
        else:
            with open(filename, 'w') as outfile:
                json.dump(self.data.to_dict('records'), outfile)

    def to_csv(self, filename="weights.csv", minimal=True):
        if minimal:
            self.data[['Lat', 'Long', 'hazard']].to_csv(filename)
        else:
            self.data.to_csv(filename)


"""
# Example run:

hazards = HazardWeights("my_route.csv") # my_route.csv is a csv w/ headers: Lat,Long,altitude,time
hazards.to_json("my_weights.json")
hazards.to_csv("my_weights.csv")
"""
