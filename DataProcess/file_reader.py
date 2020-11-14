
from datetime import datetime
from sgp4.tle_propagator import TlePropagator as _TlePropagator
import math
import glob
import csv
import numpy as np
import time
import os

def update_collisions_file(collisions):
    print(collisions)
    path_write = 'C:\\Users\\maxma\\Documents\\ActinSpace\\ActinSpace\\Assets\\Resources\\collisions.csv'
    with open(path_write, 'w', newline='') as write_csv:
        spamwriter = csv.writer(write_csv, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for collision in collisions:
            spamwriter.writerow(collision)

update_collisions_file([])
path = 'C:\\Users\\maxma\\Documents\\ActinSpace\\ActinSpace\\Assets\\Resources\\query.csv'
with open(path, 'r', newline='') as csvfile:

    lines = csvfile.readlines()
    print(lines)
    code = lines[0][:-2]
    start = lines[1][:-2]
    end = lines[2][:-2]

    a = datetime.strptime(start, '%m/%d/%Y %H:%M:%S%f')
    print(a)


start_date_epoch = datetime(2020, 1, 7, 5, 00, 00)
end_date_epoch = datetime(2020, 1, 7, 6, 00, 00)


path = 'C:\\Users\\maxma\\Documents\\Hackatlon\\files\\daily_tle_catalog\\*.txt'
files=glob.glob(path)
raw_datapoints = []

for file in files[-1:]:
    f=open(file, 'r')
    lines  = f.readlines()

    for line in lines:
        if len(line) == 1:  # Empty line
            pass
        else:

            if line[0] == "0":
                point = {}
                point[0] = line
            if line[0] == "1":
                point[1] = line
            if line[0] == "2":
                point[2] = line
                raw_datapoints.append(point)

    f.close()

class DataPoint:
    def __init__(self, tle_orbit):
        self.tle_orbit = tle_orbit


class Satellite:
    def __init__(self, code, int_designator):
        self.code = code
        self.datapoints = []
        self.collisions = []
        self.int_designator = int_designator
        self.status = None
        self.type = None

    def update_x(self, epoch):
        self.last_x = self.datapoints[-1].tle_orbit.get_state_teme(epoch)

    def propagate_from_to_interval(self, start, end, intervals):

        start_timestamp = datetime.timestamp(start)
        end_timestamp = datetime.timestamp(end)

        timestamps = np.linspace(start_timestamp, end_timestamp, intervals)

        xs = np.zeros((intervals,3))
        for i in range(intervals):
            date = datetime.fromtimestamp(timestamps[i])
            xs[i] = self.datapoints[-1].tle_orbit.get_state_teme(date)[:3]

        return xs

    def status_info(self):
        self.status = ""
        self.type = ""
        self.country = ""

        black_list_pre = open("black_list.txt", 'r')
        black_list = []
        for file in black_list_pre:
            black_list_2 = black_list_pre.readlines()
        for i_2 in range(len(black_list_2)):
            black_list_1 = black_list_2[i_2].split()
            value_bl = len(black_list_1)
            if value_bl == 2:
                black_list.append(float(black_list_1[0]))

        key_sat = float(self.code)
        flag = (key_sat in black_list)
        if flag == False:
            database_satellite = open("satcat.txt", "r")
            for file in database_satellite:
                data_satellite = database_satellite.readlines()

            satellite_int_luismi = satellites[self.code].int_designator[0:6]
            satellite_luismi = str(satellite_int_luismi)
            for i_1 in range(len(data_satellite)):
                data_sat = data_satellite[i_1].split()
                if satellite_luismi in data_sat:
                    status_sat = data_sat[-2]
                    if status_sat == 'D':
                        self.status += 'Status:Inactive'
                    elif status_sat == '-':
                        self.status += 'Status:Inactive'
                    elif status_sat == 'P':
                        self.status += 'Status:Partially-Active'
                    elif status_sat == '+':
                        self.status += 'Status:Active'
                    else:
                        self.status += 'Status:NA'
                    type_sat = data_sat[-3]
                    if type_sat == 'PAY':
                        self.type += 'Object:Satellite'
                    elif type_sat == 'DEB':
                        self.type += 'Object:Debris'
                        self.status = 'Status:Inactive'
                    else:
                        self.type += 'Object:Rocket-Stage'
                        self.status = 'Status:Inactive'
                    country_sat = data_sat[-1]
                    self.country += 'Country:' + str(country_sat)
        else:
            self.status += "Satellite-with-ID:" + str(key_sat) + "-has-been-deorbited"
    def get_x(self, time):
        x = self.datapoints[-1].tle_orbit.get_state_teme(time)[:3]
        return  x

    def check_collision(self, start, end, intervals):
        self.collision = ""

        start_timestamp = datetime.timestamp(start)
        end_timestamp = datetime.timestamp(end)

        timestamps = np.linspace(start_timestamp, end_timestamp, intervals)
        dt = timestamps[1] - timestamps[0]

        xs = np.zeros((intervals, 3))

        for i in range(intervals):
            date = datetime.fromtimestamp(timestamps[i])
            xs[i] = self.datapoints[-1].tle_orbit.get_state_teme(date)[:3]

            for other in satellites:
                if other != self.code:
                    x_other = satellites[other].get_x(date)
                    dist = np.linalg.norm(xs[i] - x_other)/1000

                    tol = dt * float(10.5)
                    if dist <= tol:
                        self.collisions.append([satellites[other].datapoints[-1].tle_orbit.tle.title[2:], satellites[other].code, date.strftime("%m/%d/%Y %H:%M:%S")])
                        self.collision += "Alert:" + str(satellites[other].code) + "&" + "Time:" + str(
                            date.year) + ":" + str(date.month) + ":" + str(date.day) + ":" + str(date.hour) + ":" + str(
                            date.minute) + ":" + str(date.second) + "-"
                        update_collisions_file(self.collisions)

    def identification(self):
        last_datapoint = self.datapoints[-1]
        eccentricity = last_datapoint.tle_orbit.tle.eccentricity
        inclination = last_datapoint.tle_orbit.tle.inclination
        meanmotion = last_datapoint.tle_orbit.tle.mean_motion * float(2 * math.pi / (86400))
        semimajor = float(pow(float(398600.436e9) / pow(meanmotion, 2), 1 / 3))
        perigeeargument = last_datapoint.tle_orbit.tle.perigee_argument

        apogeeradius = float(semimajor * (1 + eccentricity))
        perigeeradius = float(semimajor * (1 - eccentricity))
        timeperiod = float(2 * math.pi / meanmotion)

        Re = float(6378e3)  # m

        self.id = ""

        if Re + float(160e3) <= apogeeradius <= Re + float(2000e3) and Re + float(160e3) <= perigeeradius <= Re + float(
                2000e3):
            self.id = self.id + "LEO |"
        elif Re + float(2000e3) <= apogeeradius <= Re + float(35786e3) and Re + float(
                2000e3) <= perigeeradius <= Re + float(35786e3):
            self.id = self.id + "MEO |"
        elif float(86164.0905 - 5 * 60) < timeperiod < float(86164.0905 + 5 * 60):
            if float(42164e3 - 50e3) <= semimajor <= float(42164e3 + 50e3) and eccentricity <= float(0.025) and (
                    inclination <= float(2.5) or inclination >= float(180 - 2.5)):
                self.id = self.id + "GSO-GEO |"
            elif float(63.4 - 5) <= inclination <= float(63.4 + 5) and float(0.2) <= eccentricity <= float(0.3):
                self.id = self.id + "GSO-HEO-Tundra Orbit |"
                print(self.id)
            elif float(42 - 5) <= inclination <= float(42 + 5) and float(42164e3 - 50e3) <= semimajor <= float(
                    42164e3 + 50e3) and float(0.075 - 0.025) <= eccentricity <= float(0.075 + 0.025):
                self.id = self.id + "GSO-Quasi Zenith Orbit |"
            else:
                self.id = self.id + "GSO |"
        elif timeperiod > float(86164.0905 + 5 * 60):
            if float(42464e3 - 50e3) <= semimajor <= float(42464e3 + 50e3) and eccentricity <= float(0.025) and (
                    inclination <= float(7.4) or inclination >= float(180 - 7.4)):
                self.id = self.id + "High Earth Orbit-Graveyard Orbit |"
            else:
                self.id = self.id + "High Earth Orbit |"

        if float(2.5) <= inclination <= float(180 - 2.5):
            if float(90 - 2.5) <= inclination <= float(90 + 2.5):
                self.id = self.id + "Inclined Orbit-Polar Orbit |"
            elif Re + float(600e3) <= apogeeradius <= Re + float(800e3) and Re + float(
                    600e3) <= perigeeradius <= Re + float(800e3) and float(98 - 2.5) <= inclination <= float(98 + 2.5):
                self.id = self.id + "Inclined Orbit-SSO |"
            else:
                self.id = self.id + "Inclined Orbit |"
        else:
            self.id = self.id + "Non-Inclined Orbit |"

        if float(0.74 - 0.025) <= eccentricity <= float(0.74 + 0.025) and float(63.4 - 2.5) <= inclination <= float(
                63.4 + 2.5) and float(270 - 2.5) <= perigeeargument <= float(270 + 2.5):
            self.id = self.id + "HEO-Molniya Orbit |"





satellites = {}

for raw_datapoint in raw_datapoints:
    tle_orbit = _TlePropagator.from_lines([raw_datapoint[0],raw_datapoint[1],raw_datapoint[2]])
    datapoint = DataPoint(tle_orbit)

    code = tle_orbit.tle.code

    if tle_orbit.tle.code in satellites:

        satellite = satellites[code]
        satellite.datapoints.append(datapoint)
    else:
        satellite = Satellite(code, tle_orbit.tle.int_designator)
        satellites[code] = satellite
        satellite.datapoints.append(datapoint)

satellites[50].check_collision(start_date_epoch, end_date_epoch, 100)



for satellite in satellites.values():
    satellite.update_x(start_date_epoch)
    satellite.identification()
only = [50,53,5]
for satellite in only:
    print(satellite)

    satellites[satellite].status_info()














for i in range(1):
    with open('C:\\Users\\maxma\\Documents\\ActinSpace\\ActinSpace\\Assets\\Resources\\parameters.csv', 'w', newline='') as csvfile:
        print("hello")
        csvfile.truncate()
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for code in satellites:
            satellite = satellites[code]
            x = satellite.last_x

            x = list(x)
            x.append(satellite.code)
            x.append(satellite.datapoints[-1].tle_orbit.tle.eccentricity)
            x.append(satellite.datapoints[-1].tle_orbit.tle.inclination)
            x.append(satellite.datapoints[-1].tle_orbit.tle.RAAN)
            x.append(satellite.datapoints[-1].tle_orbit.tle.perigee_argument)
            x.append(satellite.datapoints[-1].tle_orbit.tle.mean_anomaly)
            x.append(satellite.datapoints[-1].tle_orbit.tle.mean_motion)
            x.append(satellite.datapoints[-1].tle_orbit.tle.title[2:])
            x.append(satellite.id)
            if satellite.status != None:
                x.append(satellite.status[7:])
                x.append(satellite.type[7:])
            else:
                x.append("nan")
                x.append("nan")
            spamwriter.writerow(x)


while True:

    path = 'C:\\Users\\maxma\\Documents\\ActinSpace\\ActinSpace\\Assets\\Resources\\query.csv'

    access = os.access('C:\\Users\\maxma\\Documents\\ActinSpace\\ActinSpace\\Assets\\Resources\\query.csv', os.R_OK)
    if access:
        with open(path, 'r', newline='') as csvfile:
            lines = csvfile.readlines()
            if len(lines)>1:
                code_new = lines[0][:-2]
                if code_new != code:
                    code = code_new
                    start = lines[1][:-2]
                    end = lines[2][:-2]
                    print(lines)

                    start = datetime.strptime(start, '%m/%d/%Y %H:%M:%S%f')
                    end = datetime.strptime(end, '%m/%d/%Y %H:%M:%S%f')

                    path_write = 'C:\\Users\\maxma\\Documents\\ActinSpace\\ActinSpace\\Assets\\Resources\\project.csv'
                    access_write = os.access(path_write, os.W_OK)
                    if access_write:
                        with open(path_write, 'w', newline='') as write_csv:
                            spamwriter = csv.writer(write_csv, delimiter=',',
                                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

                            X = satellites[int(code)].propagate_from_to_interval(start,end, 100)

                            for i in range(100):
                                spamwriter.writerow(X[i, :])
    time.sleep(.5)





