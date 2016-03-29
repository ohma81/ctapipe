import argparse

import pyhessio
from matplotlib import pyplot as plt

from ctapipe import visualization, io
from ctapipe.io.hessio import hessio_event_source
from ctapipe.reco.hillas import hillas_parameters
from ctapipe.reco.cleaning import tailcuts_clean
from ctapipe.utils.datasets import get_example_simtelarray_file

"""
Test script for the mono reconstruction

TODO:
-----

- This script is not working yet and also not yet set up to work as a proper
pytest.
"""

def get_mc_calibration_coeffs(tel_id):
    """
    Get the calibration coefficients from the MC data file to the
    data.  This is a hack (until we have a real data structure for the
    calibrated data), it should move into `ctapipe.io.hessio_event_source`.

    returns
    -------
    (peds,gains) : arrays of the pedestal and pe/dc ratios.
    """
    peds = pyhessio.get_pedestal(tel_id)[0]
    gains = pyhessio.get_calibration(tel_id)[0]
    return peds, gains


def apply_mc_calibration(adcs, tel_id):
    """
    apply basic calibration
    """
    peds, gains = get_mc_calibration_coeffs(tel_id)
    return (adcs - peds) * gains


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='test mono reconstruction')
    parser.add_argument('telid', metavar='TEL_ID', type=int)
    parser.add_argument('filename', metavar='EVENTIO_FILE', nargs='?',
                        default=get_example_simtelarray_file())
    parser.add_argument('-m', '--max-events', type=int, default=100000)
    args = parser.parse_args()

    #def test_monoreco():
    source = hessio_event_source(args.filename,
                                 allowed_tels=[args.telid, ],
                                 max_events=args.max_events)

    disp = None

    print('SELECTING EVENTS FROM TELESCOPE {}'.format(args.telid))

    for event in source:

        print('Scanning input file... count = {}'.format(event.count))
        print(event.trig)
        print(event.mc)
        print(event.dl0)

        if disp is None:
            x, y = event.meta.pixel_pos[args.telid]
            geom = io.CameraGeometry.guess(x, y, event.meta.optical_foclen[args.telid])
            disp = visualization.CameraDisplay(geom, title='CT%d' % args.telid)
            disp.enable_pixel_picker()
            disp.add_colorbar()
            plt.show(block=False)

        # calibrate and display integrated event:
        image = event.dl0.tel[args.telid].adc_sums[0]
        image = apply_mc_calibration(image, args.telid)

        # apply tailcuts cleaning
        camera_mask = tailcuts_clean(geom, image, 1, 14, 6) # values already in pe
        image[~camera_mask] = 0
        disp.image = image
        # calculate image parameters
        hillas = hillas_parameters(geom.pix_x.value, geom.pix_y.value, image)
        print(hillas)

        disp.overlay_moments(hillas, color='seagreen', linewidth=3)

        plt.pause(0.1)
