#!/usr/bin/env  python
# -*- coding: utf -8  -*-
""" Collection of functions for TLE propagation and estimation
   ===========================================================
"""

__author__ = "Mirco Calura"
__maintainer__ = "Matteo Aquilano"
__copyright__ = "Copyright 2020 by SES  ENGINEERING S.A. All  Rights  Reserved"
__version__ = "00.00"

# Last  Modified:
#
# 10-Nov-2020 MA 00.00 Adjusted for AIS 2020


import math

import numpy as _np

_GM_earth = 398600.436e9  # Earth gravitational constant [m^3/s^2]
RE = 6378.137e3  # Earth radius [m]


def eccentric_to_mean(d_eta, d_e):

    d_mean = d_eta - d_e * math.sin(d_eta)

    return d_mean


def eccentric_to_true(d_eta, d_e):

    d_true = 2.*math.atan(math.sqrt((1. + d_e)/(1. - d_e))*math.tan(d_eta/2.))

    return d_true


def mean_to_eccentric(d_mean, d_e):

    d_toll = 1.e-10

    d_Eta_0 = d_mean

    Delta_Eta = (d_mean - d_Eta_0 + d_e*math.sin(d_Eta_0)) / \
        (1. - d_e*math.cos(d_Eta_0))
    Eta = d_Eta_0 + Delta_Eta

    while(math.fabs(Delta_Eta) >= d_toll):
        d_Eta_0 = Eta
        Delta_Eta = (d_mean - d_Eta_0 + d_e*math.sin(d_Eta_0)) / \
            (1. - d_e*math.cos(d_Eta_0))
        Eta = d_Eta_0 + Delta_Eta

    Eta = d_Eta_0 + Delta_Eta

    return Eta


def true_to_eccentric(d_true, d_e):

    Eta = 2.*math.atan(math.sqrt((1. - d_e)/(1. + d_e))*math.tan(d_true/2.))

    return Eta


def true_to_mean(d_true, d_e):

    Eta = true_to_eccentric(d_true, d_e)

    return eccentric_to_mean(Eta, d_e)


def mean_to_true(d_mean, d_e):

    Eta = mean_to_eccentric(d_mean, d_e)

    return eccentric_to_true(Eta, d_e)


def cartesian_to_elements(S):

    E = [0.]*7

    C1 = S[1]*S[5]-S[2]*S[4]
    C2 = S[2]*S[3]-S[0]*S[5]
    C3 = S[0]*S[4]-S[1]*S[3]

    CC12 = C1*C1+C2*C2
    CC = CC12 + C3*C3
    C = math.sqrt(CC)

    V02 = math.pow(S[3], 2.)+math.pow(S[4], 2.)+math.pow(S[5], 2.)
    R0V0 = S[0]*S[3]+S[1]*S[4]+S[2]*S[5]
    R02 = math.pow(S[0], 2.)+math.pow(S[1], 2.)+math.pow(S[2], 2.)

    R0 = math.sqrt(R02)
    X = R0*V02/_GM_earth
    CX = CC/_GM_earth
    STE = R0V0*C/(R0*_GM_earth)
    CTE = CX/R0-1.
    E[0] = R0/(2.-X)
    E[1] = math.sqrt(STE*STE+CTE*CTE)
    E[2] = math.atan2(math.sqrt(CC12), C3)

    if(CC12 > CC*(1.e-20)):

        U = math.atan2(C*S[2], S[1]*C1-S[0]*C2)
        E[3] = math.atan2(C1, -C2)

        if(E[1] > 1.e-20):
            E[5] = math.atan2(STE, CTE)
            E[4] = U - E[5]
        else:
            E[5] = U
            E[4] = 0.

    else:

        d_sign = 1.

        if(C3 < 0.):
            d_sign = -1.

        U = math.atan2(S[1], S[0])*d_sign
        E[3] = 0.

        if(E[1] > 1.e-20):
            E[5] = math.atan2(STE, CTE)
            E[4] = U - E[5]
        else:
            E[5] = U
            E[4] = 0.

    if(E[3] < 0.):
        E[3] += (2.*math.pi)
    if(E[4] < 0.):
        E[4] += (2.*math.pi)
    if(E[5] < 0.):
        E[5] += (2.*math.pi)

    E[6] = S[6]

    E[0] = math.sqrt(_GM_earth/math.pow(E[0], 3.))*86400./(2.*math.pi)

    E[5] = true_to_mean(E[5], E[1])

    return E


def elements_to_cartesian(E):

    E[0] = math.pow(_GM_earth/math.pow(2.*math.pi/86400.*E[0], 2.), 1./3.)

    E5_true = mean_to_true(E[5], E[1])

    p = E[0]*(1.-math.pow(E[1], 2.))

    if(p < (1.e-30)):
        p = 1.e-30

    F = math.sqrt(_GM_earth)/math.sqrt(p)

    CV = math.cos(E5_true)
    ECV = 1. + E[1]*CV
    R = p/ECV
    U = E[4] + E5_true
    CU = math.cos(U)
    SU = math.sin(U)
    CO = math.cos(E[3])
    SO = math.sin(E[3])
    CI = math.cos(E[2])
    SI = math.sin(E[2])
    COCU = CO*CU
    SOSU = SO*SU
    SOCU = SO*CU
    COSU = CO*SU

    FX = COCU - SOSU*CI
    FY = SOCU + COSU*CI
    FZ = SU*SI
    VR = F*E[1]*math.sin(E5_true)
    VU = F*ECV

    S = [0.]*7

    S[0] = R*FX
    S[1] = R*FY
    S[2] = R*FZ
    S[3] = VR*FX - VU*(COSU + SOCU*CI)
    S[4] = VR*FY - VU*(SOSU - COCU*CI)
    S[5] = VR*FZ + VU*CU*SI

    S[6] = E[6]

    return S


# Retrieve a raw estimation of orbit summary parameters
def get_orbit_summary(x):

    elem = cartesian_to_elements(_np.append(x, [0.]))

    d_a = math.pow(_GM_earth/math.pow(2.*math.pi/86400.*elem[0], 2.), 1./3.)

    d_e = elem[1]

    d_T = 2.*math.pi/math.sqrt(_GM_earth/math.pow(d_a, 3.))

    # Raw estimate of the altitude of perigee (km)
    d_per_alt = d_a*(1. - d_e) - RE

    return d_per_alt, d_T


def get_line_code(s_line):

    if(len(s_line) < 69):
        return None

    i_code = int(s_line[2:7])

    return i_code
