#!/usr/bin/env  python
# -*- coding: utf -8  -*-
"""Class managing TLE propagation
   ==============================
"""

__author__ = "Mirco Calura"
__maintainer__ = "Matteo Aquilano"
__copyright__ = "Copyright 2020 by SES  ENGINEERING S.A. All  Rights  Reserved"
__version__ = "00.00"

# Last  Modified:
#
# 10-Nov-2020 MA 00.00 Adjusted for AIS 2020


import math
from datetime import datetime, timedelta

import numpy as _np

from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv_sat
from sgp4.tle_lib import cartesian_to_elements, elements_to_cartesian, \
    get_line_code
import sgp4.tle_utility as tle_ut


class TlePropagator(object):

    def __init__(self):

        self.tle = None  # this is the TleCreator object

        # Lines of the file which could represent the set
        self.Line_0 = None
        self.Line_1 = None
        self.Line_2 = None

        # additional parameters
        self.satellite = None

        return

    # Create a TLE propagator from a TLECreator
    @classmethod
    def from_tle_creator(cls, tle):

        self = object.__new__(cls)

        self.Line_0 = tle.title
        self.Line_1 = tle.first_line
        self.Line_2 = tle.second_line

        self.tle = tle

        self.initialize_propagator()

        return self

    # Create a TLE propagator from a mean cartesian state vector
    @classmethod
    def from_mean_cartesian(cls, code, epoch, bstar, x_mean, name=None,
                            int_designator=None, classification=None,
                            mean_motion_dot=None, mean_motion_ddot=None,
                            elset_type=None, elset_num=None, nrevs=None):

        self = object.__new__(cls)

        self.Line_0 = None
        self.Line_1 = None
        self.Line_2 = None

        # y_mean = x_mean + [bstar]
        y_mean = _np.append(x_mean, [bstar])

        s = cartesian_to_elements(y_mean)

        inclination = math.degrees(s[2])
        raan = math.degrees(s[3])
        eccentricity = s[1]
        perigee = math.degrees(s[4])
        anomaly = math.degrees(s[5])
        motion = s[0]
        bstar = s[6]

        if name is None:
            self.Line_0 = 'SAT_' + str(code)
        else:
            self.Line_0 = name

        self.Line_1 = \
            tle_ut.data_to_first_line(code, epoch, bstar,
                                      classification=classification,
                                      int_designator=int_designator,
                                      mean_motion_dot=mean_motion_dot,
                                      mean_motion_ddot=mean_motion_ddot,
                                      elset_type=elset_type,
                                      elset_num=elset_num)
        self.Line_2 = \
            tle_ut.data_to_second_line(code, inclination, raan, eccentricity,
                                       perigee, anomaly, motion, nrevs=nrevs)

        self.tle = tle_ut.TLECreator.from_str(
            self.Line_1, self.Line_2, line_0=self.Line_0)

        self.initialize_propagator()

        return self

    # Create a TLE propagator from an array of 2 (or 3) lines
    @classmethod
    def from_lines(cls, lines):

        i_num = len(lines)
        if(i_num < 2):
            raise ValueError('ERROR: you must provide at least two lines')

        line0 = None
        line1 = None
        line2 = None
        for line in lines:
            if tle_ut.is_first_line(line):
                line1 = line
            elif tle_ut.is_second_line(line):
                line2 = line
            else:
                line0 = line
        if line1 is None:
            raise ValueError('ERROR: TLE first line is not valid')
        if line2 is None:
            raise ValueError('ERROR: TLE second line is not valid')

        tle = tle_ut.TLECreator.from_str(line1, line2, line_0=line0)

        self = cls.from_tle_creator(tle)

        return self

    # Create a TLE propagator reading the parameters from an external file.
    # If the file contains multiple TLEs the one with the specified code
    # is used. If no code is specified the first paramters set are considered
    @classmethod
    def from_multi_tle_file(cls, s_file_path, code=None):

        f_tle = open(s_file_path)

        l_all_lines = f_tle.readlines()

        f_tle.close()

        l_lines = []

        # Remove all the comment lines
        for s_line in l_all_lines:
            s_line = s_line.strip()
            if(len(s_line) > 0):
                if(s_line[0:1] != '#'):
                    l_lines.append(s_line)

        l_lines_0 = []
        l_lines_1 = []
        l_lines_2 = []

        for s_line in l_lines:
            s_line = s_line.strip()
            if tle_ut.is_first_line(s_line):
                l_lines_1.append(s_line)
            elif tle_ut.is_second_line(s_line):
                l_lines_2.append(s_line)
            else:
                l_lines_0.append(s_line)

        i_num_tles = len(l_lines_1)

        if(i_num_tles < 1):
            raise ValueError('ERROR: TLE file is not valid')

        if(len(l_lines_2) < i_num_tles):
            raise ValueError('ERROR: TLE file is not valid')

        b_found = False
        line0 = None
        line1 = None
        line2 = None

        # Start loop over tles
        for i in range(0, i_num_tles):
            i_code_1 = get_line_code(l_lines_1[i])
            i_code_2 = get_line_code(l_lines_2[i])
            if i_code_1 is None:
                raise ValueError('ERROR: TLE file is not valid')
            if i_code_2 is None:
                raise ValueError('ERROR: TLE file is not valid')
            if i_code_1 != i_code_2:
                raise ValueError('ERROR: TLE file is not valid')
            if code is None:
                line1 = l_lines_1[i]
                line2 = l_lines_2[i]
                if(len(l_lines_0) == i_num_tles):
                    line0 = l_lines_0[i]
                else:
                    line0 = None
                b_found = True
                break
            else:
                if(i_code_1 == code):
                    line1 = l_lines_1[i]
                    line2 = l_lines_2[i]
                    if(len(l_lines_0) == i_num_tles):
                        line0 = l_lines_0[i]
                    else:
                        line0 = None
                    b_found = True
                    break
        # End loop over tles

        if(not b_found):
            return None

        self = cls.from_lines([line0, line1, line2])

        return self

    # For TLE there is not clear definition of validity start. Here it is taken
    # a reference value to make th eobjace usable in place of orbit as well
    def get_first_epoch(self):

        return self.tle.epoch - 10.

    # For TLE there is not clear definition of validity stop. Here it is taken
    # a reference value to make th eobjace usable in place of orbit as well
    def get_last_epoch(self):

        return self.tle.epoch + 10.

    # Retrieve state vector at given epoch with respect to
    # True Equator & Mean Equinox frame.
    # Position is in meters and velocity in meters/sec
    def get_state_teme(self, epoch):

        x = _np.zeros(6)

        i_year = epoch.year
        i_month = epoch.month
        i_day = epoch.day
        i_hour = epoch.hour
        i_min = epoch.minute
        d_sec = epoch.second + epoch.microsecond/1000000.

        try:
            position, velocity = \
                self.satellite.propagate(i_year, i_month, i_day,
                                         i_hour, i_min, d_sec)
        except BaseException:
            raise ValueError('ERROR: impossible to propagate TLE')

        for k in range(0, 3):
            x[k] = position[k]*1e3
            x[3 + k] = velocity[k]*1e3

        return x

    # Compute the parameters of the SGP4 propagator
    def initialize_propagator(self):

        i_ref_year = self.tle.epoch.year

        epoch_0 = datetime(i_ref_year, 1, 1)

        d_ref_doy = (self.tle.epoch - epoch_0 +
                     timedelta(days=1)).total_seconds() / 86400.

        d_ndot = 0.
        d_nddot = 0.
        i_nexp = 0

        d_bstar_base = self.tle.bstar
        i_ibexp = 0.

        i_ref_year_2_digits = i_ref_year - 2000

        try:
            self.satellite = twoline2rv_sat(self.tle.code, i_ref_year_2_digits,
                                            d_ref_doy, d_ndot, d_nddot, i_nexp,
                                            d_bstar_base, i_ibexp,
                                            self.tle.inclination,
                                            self.tle.RAAN,
                                            self.tle.eccentricity,
                                            self.tle.perigee_argument,
                                            self.tle.mean_anomaly,
                                            self.tle.mean_motion,
                                            wgs72, afspc_mode=True)
        except BaseException:
            raise ValueError('ERROR: impossible to process TLE data')

        return

    # Retrieve TLE state in mean cartesian format (m, m/sec)
    def to_mean_cartesian(self):

        y = [0.]*6

        inc = math.radians(self.tle.inclination)
        W = math.radians(self.tle.RAAN)
        ecc = self.tle.eccentricity
        w = math.radians(self.tle.perigee_argument)
        M = math.radians(self.tle.mean_anomaly)
        n = self.tle.mean_motion

        y = elements_to_cartesian([n, ecc, inc, W, w, M, self.tle.bstar])

        x = y[0:6]

        return x

    # Return lines of the TLE
    def get_lines(self, offset=None):

        l_lines = []

        if(self.Line_0 is not None):
            l_lines.append(self.Line_0)

        l_lines.append(self.Line_1)

        if(offset is None):

            l_lines.append(self.Line_2)

        else:

            i_act_code, d_act_i, d_act_W, d_act_e, d_act_w, d_act_M, d_act_n, \
                _ = tle_ut.second_line_to_data(self.Line_2)

            d_act_M += math.degrees(offset)

            s_line = tle_ut.data_to_second_line(i_act_code, d_act_i, d_act_W,
                                                d_act_e, d_act_w, d_act_M,
                                                d_act_n)

            l_lines.append(s_line)

        return l_lines

    # Return list of norad ids in the TLE
    def get_codes_from_file(self, s_file_path):

        f_tle = open(s_file_path)

        l_all_lines = f_tle.readlines()

        f_tle.close()

        l_lines = []

        # Remove all the comment lines
        for s_line in l_all_lines:
            s_line = s_line.strip()
            if(len(s_line) > 0):
                if(s_line[0:1] != '#'):
                    l_lines.append(s_line)

        l_lines_1 = []
        l_lines_2 = []

        for s_line in l_lines:
            s_line = s_line.strip()
            if tle_ut.is_first_line(s_line):
                l_lines_1.append(s_line)
            elif tle_ut.is_second_line(s_line):
                l_lines_2.append(s_line)
            else:
                pass

        i_num_tles = len(l_lines_1)

        if(i_num_tles < 1):
            raise ValueError('ERROR: TLE file is not valid')

        if(len(l_lines_2) < i_num_tles):
            raise ValueError('ERROR: TLE file is not valid')

        # Start loop over tles
        codes = []
        for i in range(0, i_num_tles):
            i_code_1 = get_line_code(l_lines_1[i])
            i_code_2 = get_line_code(l_lines_2[i])
            if(i_code_1 is None):
                raise ValueError('ERROR: TLE file is not valid')
            if(i_code_2 is None):
                raise ValueError('ERROR: TLE file is not valid')
            if(i_code_1 != i_code_2):
                raise ValueError('ERROR: TLE file is not valid')
            codes.append(i_code_1)

        return codes
