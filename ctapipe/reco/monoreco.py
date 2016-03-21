"""Disp method based direction reconstruction


assume phi is good angle


"""

import numpy as np
import hillas
from astropy.units import Quantity
from collections import namedtuple

__all__ = [
    'MonoDirections',
]

MonoDirections = namedtuple(
    "MonoDirections",
    "pos_x,pos_y,pos_xx,pos_yy"
)


def disp_value(hillas_parameters):
    """Compute Disp value

	Parameters
	----------
	hillas_parameters: namedtuple
	
	
	Returns	
	-------
	disp
	
	"""

    w = hillas_parameters.width
    l = hillas_parameters.length

    disp = 1 - w / l

    return disp


def source_position(hillas_parameters, disp):
    """Compute direction of shower

	Parameters
	-----   -----
	phi: float
		angle between camera x axis and main hillas axis
	cen_x: float
	cen_y: float
		center of the ellipse
	
	disp: float
		disp value

	Returns
	-------

	position : x and y
	"""
    phi = hillas_parameters.phi
    cen_x = hillas_parameters.cen_x
    cen_y = hillas_parameters.cen_y

    x = np.cos(phi) * disp + cen_x
    y = np.sin(phi) * disp + cen_y

    xx = cen_x - np.cos(phi) * disp
    yy = cen_y - np.sin(phi) * disp

    return MonoDirections(pos_x=x, pos_y=y, pos_xx=xx, pos_yy=yy)
