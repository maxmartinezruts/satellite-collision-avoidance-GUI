#!/usr/bin/env  python
# -*- coding: utf -8  -*-
"""Class managing input/output of data in TLE format
   =================================================
"""

__author__ = "Mirco Calura"
__maintainer__ = "Matteo Aquilano"
__copyright__ = "Copyright 2020 by SES ENGINEERING S.A. All  Rights  Reserved"
__version__ = "00.00"

# Last  Modified:
#
# 10-Nov-2020 MA 00.00 Adjusted for AIS 2020


import math
from datetime import datetime, timedelta


class TLECreator(object):

    def __init__(self, title=None, code=None, classification=None,
                 int_designator=None, epoch=None, mean_motion_dot=None,
                 mean_motion_ddot=None, bstar=None, elset_type=None,
                 elset_num=None, inclination=None, RAAN=None,
                 eccentricity=None, perigee_argument=None, mean_anomaly=None,
                 mean_motion=None, nrevs=None):

        self.title = title
        self.code = code
        self.classification = classification
        self.int_designator = int_designator
        self.epoch = epoch
        self.mean_motion_dot = mean_motion_dot
        self.mean_motion_ddot = mean_motion_ddot
        self.bstar = bstar
        self.elset_type = elset_type
        self.elset_num = elset_num
        self.inclination = inclination
        self.RAAN = RAAN
        self.eccentricity = eccentricity
        self.perigee_argument = perigee_argument
        self.mean_anomaly = mean_anomaly
        self.mean_motion = mean_motion
        self.nrevs = nrevs

        return

    @classmethod
    def from_file(cls, s_file_path, title=None):
        """Creates a new instance of this class reading the information from
        a TLE text file.

        Parameters:
        -----------
        s_file_path: str
            Filepath to the TLE file
        """

        self = object.__new__(cls)
        with open(s_file_path, 'r') as f_in:
            lines = f_in.readlines()

        for line in lines:
            if is_first_line(line):
                self.code, self.classification, self.int_designator, \
                    self.epoch, self.mean_motion_dot, self.mean_motion_ddot, \
                    self.bstar, self.elset_type, self.elset_num = \
                    first_line_to_data(line)
            elif is_second_line(line):
                _, self.inclination, self.RAAN, self.eccentricity, \
                    self.perigee_argument, self.mean_anomaly, \
                    self.mean_motion, self.nrevs = second_line_to_data(line)
        self.title = title
        if self.title is None and len(lines) > 2:
            # if there are threee lines the first one should be the title
            self.title = lines[0].strip()

        return self

    def to_file(self, s_file_path):
        """Writes a TLE text file.

        Parameters:
        -----------
        s_file_path: str
            Filepath to the TLE file
        """

        line_0, line1, line2 = self.to_str()
        with open(s_file_path, 'w') as f_out:
            if line_0 is not None:  # three-line-element
                f_out.write(line_0 + "\n")
            f_out.write(line1 + "\n")
            f_out.write(line2 + "\n")

        return

    @classmethod
    def from_str(cls, line_1, line_2, line_0=None):
        """Initialize from the string representation of the TLE

        Parameters:
        -----------
        line_1: str
            TLE first line

        line_2: str
            TLE second line
        """
        self = object.__new__(cls)

        self.code, self.classification, self.int_designator, self.epoch, \
            self.mean_motion_dot, self.mean_motion_ddot, self.bstar, \
            self.elset_type, self.elset_num = first_line_to_data(line_1)
        self.code, self.inclination, self.RAAN, self.eccentricity, \
            self.perigee_argument, self.mean_anomaly, self.mean_motion, \
            self.nrevs = second_line_to_data(line_2)
        self.title = None
        if line_0 is not None:
            self.title = line_0.strip()

        return self

    def to_str(self):
        """Return the two strings corresponding the the TLE file content"""
        line_1 = data_to_first_line(self.code, self.epoch, self.bstar,
                                    classification=self.classification,
                                    int_designator=self.int_designator,
                                    mean_motion_dot=self.mean_motion_dot,
                                    mean_motion_ddot=self.mean_motion_ddot,
                                    elset_type=self.elset_type,
                                    elset_num=self.elset_num)
        line_2 = data_to_second_line(self.code, self.inclination, self.RAAN,
                                     self.eccentricity, self.perigee_argument,
                                     self.mean_anomaly, self.mean_motion,
                                     nrevs=self.nrevs)
        line_0 = self.title

        return line_0, line_1, line_2

    @property
    def first_line(self):
        _, line1, _ = self.to_str()
        return line1

    @property
    def second_line(self):
        _, _, line2 = self.to_str()
        return line2


def get_check_sum(s_line):

    i_check_sum = 0

    for s in s_line:
        if(s == '-'):
            i_check_sum += 1
        else:
            if(s.isdigit()):
                i_check_sum += int(s)

    i_check_sum = i_check_sum % 10

    return i_check_sum


def first_line_to_data(s_line):

    Code = int(s_line[2:7])

    classification = s_line[7:8]

    int_des = (s_line[9:17])

    i_year = 2000 + int(s_line[18:20])

    d_doy = float(s_line[20:32])

    epoch = datetime(i_year, 1, 1) + timedelta(days=d_doy-1)

    mean_motion_dot = float(s_line[33:43])

    mmdd_base = s_line[44:50].strip()
    if mmdd_base.startswith("+"):
        d_mmdd_base = float("0." + mmdd_base.replace("+", ""))
    elif mmdd_base.startswith("-"):
        d_mmdd_base = float("-0." + mmdd_base.replace("-", ""))
    else:
        d_mmdd_base = float("0." + mmdd_base)
    d_mmdd_exp = float(s_line[50:52])
    mean_motion_ddot = d_mmdd_base*math.pow(10.0, d_mmdd_exp)

    b_base = s_line[53:59].strip()
    if b_base.startswith("+"):
        d_b_base = float("0." + b_base.replace("+", ""))
    elif b_base.startswith("-"):
        d_b_base = float("-0." + b_base.replace("-", ""))
    else:
        d_b_base = float("0." + b_base)
    d_b_exp = float(s_line[59:61])
    Bstar = d_b_base * math.pow(10.0, d_b_exp)

    elset_type = s_line[62:63]

    elset_num = int(s_line[64:68])

    check_sum = int(s_line[68:69])
    i_chk = get_check_sum(s_line[:68])
    if check_sum != i_chk:
        print("WARNING - tle_utility first_line_to_data()\n"
              "Invalid check_sum for line: '" + s_line + "'")

    return Code, classification, int_des, epoch, mean_motion_dot, \
        mean_motion_ddot, Bstar, elset_type, elset_num


def second_line_to_data(s_line):

    Code = int(s_line[2:7])

    Inclination = float(s_line[8:16])

    RAAN = float(s_line[17:25])

    Eccentricity = float(s_line[26:33])*(1e-7)

    PerigeeArgument = float(s_line[34:42])

    MeanAnomaly = float(s_line[43:51])

    MeanMotion = float(s_line[52:63])

    Nrevs = float(s_line[64:68])

    check_sum = int(s_line[68:69])
    i_chk = get_check_sum(s_line[:68])
    if check_sum != i_chk:
        print("WARNING - tle_utility second_line_to_data()\n"
              "Invalid check_sum for line: '" + s_line + "'")

    return Code, Inclination, RAAN, Eccentricity, PerigeeArgument, \
        MeanAnomaly, MeanMotion, Nrevs


def data_to_first_line(code, epoch, bstar, classification=None,
                       int_designator=None, mean_motion_dot=None,
                       mean_motion_ddot=None, elset_type=None, elset_num=None):

    s_code = ('%05i' % code)

    i_year = epoch.year

    epoch_0 = datetime(i_year, 1, 1)

    d_doy = (epoch - epoch_0 + timedelta(days=1)).total_seconds() / 86400.

    if(i_year >= 2000):
        i_y = i_year - 2000
    else:
        i_y = i_year - 1950

    s_epoch = ('%2i%012.8f') % (i_y, d_doy)

    if(bstar > 0.):
        i_bstar_sign = 1
    else:
        i_bstar_sign = -1

    d_bstar = math.fabs(bstar)  # /100000.

    if(d_bstar < 1e-10):

        d_bstar = 0.
        i_exp_bstar = 0
        i_bstar = 0
        i_exp_bstar = 0

    else:

        i_exp_bstar = int(math.floor(math.log10(d_bstar)))
        d_base = d_bstar*math.pow(10., -i_exp_bstar + 4)
        i_bstar = int(d_base)
        i_exp_bstar = i_exp_bstar + 1
        i_bstar = i_bstar_sign*i_bstar

    if(i_bstar >= 0):
        if(i_exp_bstar <= 0):
            s_bstar = (' %05i-%i') % (i_bstar, -i_exp_bstar)
        else:
            s_bstar = (' %05i %i') % (i_bstar, i_exp_bstar)
    else:
        if(i_exp_bstar <= 0):
            s_bstar = ('-%05i-%i') % (-i_bstar, -i_exp_bstar)
        else:
            s_bstar = ('-%05i %i') % (-i_bstar, i_exp_bstar)

    if(int_designator is None):
        s_int_des = '000000'
    else:
        s_int_des = int_designator

    if(classification is None):
        s_class = 'U'
    else:
        s_class = classification[0]

    if mean_motion_dot is None:
        mmd = "+.00000000"
    else:
        mmd = "{:+.8f}".format(mean_motion_dot).replace("0", "", 1)

    if mean_motion_ddot is None:
        mmdd = "00000-0"
    else:
        exp_rep = "{:.4e}".format(mean_motion_ddot)
        a, b = exp_rep.split("e")
        mmdd_0 = a.replace(".", "")
        mmdd_1 = int(b) - 1
        mmdd = mmdd_0 + "{:+1d}".format(mmdd_1)

    if elset_type is None:
        elset_type = 0

    if elset_num is None:
        elset_num = 0

    s_int_des = s_int_des + (' '*6)
    s_int_des = s_int_des[0:6]

    s_line = '1 ' + s_code + s_class + ' ' + s_int_des + '   ' + s_epoch + \
        ' ' + mmd + '  ' + mmdd + ' ' + s_bstar + \
        ' ' + "{:1d}".format(int(elset_type)) + ' ' + \
        "{:4d}".format(int(elset_num))

    i_chk = get_check_sum(s_line)

    s_line = s_line + str(i_chk)

    return s_line


def get_adjusted_angle(d_ang, cycle=360.):

    d_ang = math.fmod(d_ang, cycle)

    if(d_ang < 0.):
        d_ang = d_ang + cycle

    return d_ang


def data_to_second_line(code, inclination, RAAN, eccentricity,
                        perigee_argument, mean_anomaly, mean_motion,
                        nrevs=None):

    s_code = ('%05i' % code)

    s_inclination = ('%9.4f') % (get_adjusted_angle(inclination))

    s_raan = ('%9.4f') % (get_adjusted_angle(RAAN))

    s_eccentricity = ('%07i') % (eccentricity*(1e7))

    s_perigee_arg = ('%9.4f') % (get_adjusted_angle(perigee_argument))

    s_mean_anomaly = ('%9.4f') % (get_adjusted_angle(mean_anomaly))

    s_mean_motion = ('%12.8f') % (get_adjusted_angle(mean_motion))

    if nrevs is None:
        nrevs = 0

    s_line = '2 ' + s_code + s_inclination + s_raan + ' ' + s_eccentricity \
        + s_perigee_arg + s_mean_anomaly + s_mean_motion + ' ' + \
        "{:4d}".format(int(nrevs))

    i_chk = get_check_sum(s_line)

    s_line = s_line + str(i_chk)

    return s_line


def is_first_line(s_line):

    if(len(s_line) < 69):
        return False

    if(s_line[0:2] != '1 '):
        return False

    return True


def is_second_line(s_line):

    if(len(s_line) < 69):
        return False

    if(s_line[0:2] != '2 '):
        return False

    return True
