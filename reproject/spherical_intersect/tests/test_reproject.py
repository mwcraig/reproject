# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.utils.data import get_pkg_data_filename

from ..core import _reproject_celestial


def test_reproject_celestial_slices_2d():

    header_in = fits.Header.fromtextfile(get_pkg_data_filename('../../tests/data/gc_ga.hdr'))
    header_out = fits.Header.fromtextfile(get_pkg_data_filename('../../tests/data/gc_eq.hdr'))

    array_in = np.ones((100, 100))

    wcs_in = WCS(header_in)
    wcs_out = WCS(header_out)

    _reproject_celestial(array_in, wcs_in, wcs_out, (200, 200))

DATA = np.array([[1, 2], [3, 4]])

INPUT_HDR = """
WCSAXES =                    2 / Number of coordinate axes
CRPIX1  =              299.628 / Pixel coordinate of reference point
CRPIX2  =              299.394 / Pixel coordinate of reference point
CDELT1  =         -0.001666666 / [deg] Coordinate increment at reference point
CDELT2  =          0.001666666 / [deg] Coordinate increment at reference point
CUNIT1  = 'deg'                / Units of coordinate increment and value
CUNIT2  = 'deg'                / Units of coordinate increment and value
CTYPE1  = 'GLON-CAR'           / galactic longitude, plate caree projection
CTYPE2  = 'GLAT-CAR'           / galactic latitude, plate caree projection
CRVAL1  =                  0.0 / [deg] Coordinate value at reference point
CRVAL2  =                  0.0 / [deg] Coordinate value at reference point
LONPOLE =                  0.0 / [deg] Native longitude of celestial pole
LATPOLE =                 90.0 / [deg] Native latitude of celestial pole
"""

OUTPUT_HDR = """
WCSAXES =                    2 / Number of coordinate axes
CRPIX1  =                  2.5 / Pixel coordinate of reference point
CRPIX2  =                  2.5 / Pixel coordinate of reference point
CDELT1  =         -0.001500000 / [deg] Coordinate increment at reference point
CDELT2  =          0.001500000 / [deg] Coordinate increment at reference point
CUNIT1  = 'deg'                / Units of coordinate increment and value
CUNIT2  = 'deg'                / Units of coordinate increment and value
CTYPE1  = 'RA---TAN'           / Right ascension, gnomonic projection
CTYPE2  = 'DEC--TAN'           / Declination, gnomonic projection
CRVAL1  =        267.183880241 / [deg] Coordinate value at reference point
CRVAL2  =        -28.768527143 / [deg] Coordinate value at reference point
LONPOLE =                180.0 / [deg] Native longitude of celestial pole
LATPOLE =        -28.768527143 / [deg] Native latitude of celestial pole
EQUINOX =               2000.0 / [yr] Equinox of equatorial coordinates
"""

MONTAGE_REF = np.array([[np.nan, 2., 2., np.nan],
                        [1., 1.6768244, 3.35364754, 4.],
                        [1., 1.6461656, 3.32308315, 4.],
                        [np.nan, 3., 3., np.nan]])


def test_reproject_celestial_consistency():

    # Consistency between the different modes

    wcs_in = WCS(fits.Header.fromstring(INPUT_HDR, sep='\n'))
    wcs_out = WCS(fits.Header.fromstring(OUTPUT_HDR, sep='\n'))

    array1, footprint1 = _reproject_celestial(DATA, wcs_in, wcs_out, (4, 4), _legacy=True)
    array2, footprint2 = _reproject_celestial(DATA, wcs_in, wcs_out, (4, 4), parallel=False)
    array3, footprint3 = _reproject_celestial(DATA, wcs_in, wcs_out, (4, 4), parallel=True)

    np.testing.assert_allclose(array1, array2, rtol=1.e-6)
    np.testing.assert_allclose(array1, array3, rtol=1.e-6)

    np.testing.assert_allclose(footprint1, footprint2, rtol=1.e-6)
    np.testing.assert_allclose(footprint1, footprint3, rtol=1.e-6)


def test_reproject_celestial_():

    # Accuracy compared to Montage

    wcs_in = WCS(fits.Header.fromstring(INPUT_HDR, sep='\n'))
    wcs_out = WCS(fits.Header.fromstring(OUTPUT_HDR, sep='\n'))

    array, footprint = _reproject_celestial(DATA, wcs_in, wcs_out, (4, 4), parallel=False)

    # TODO: improve agreement with Montage - at the moment agreement is ~10%
    np.testing.assert_allclose(array, MONTAGE_REF, rtol=0.09)
