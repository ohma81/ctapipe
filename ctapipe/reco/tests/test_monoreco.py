import pyhessio
from matplotlib import pyplot as plt

from ctapipe import visualization, io
from ctapipe.io.hessio import hessio_event_source
from ctapipe.utils.datasets import get_example_simtelarray_file
from ctapipe.reco.hillas import hillas_parameters
from ctapipe.io import CameraGeometry

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
    data.  This is ahack (until we have a real data structure for the
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
#def test_monoreco():
    telid = 2
    maxevents = 1000
    source = hessio_event_source(get_example_simtelarray_file(),
                                 allowed_tels=[telid], max_events=maxevents)

    disp = None

    print('SELECTING EVENTS FROM TELESCOPE {}'.format(telid))

    for event in source:

        print('Scanning input file... count = {}'.format(event.count))
        print(event.trig)
        print(event.mc)
        print(event.dl0)

        if disp is None:
            x, y = event.meta.pixel_pos[telid]
            geom = io.CameraGeometry.guess(x, y)
            disp = visualization.CameraDisplay(geom, title='CT%d' % telid)
            disp.enable_pixel_picker()
            disp.add_colorbar()
            plt.show(block=False)

        # display integrated event:
        disp.image = apply_mc_calibration(
            event.dl0.tel[telid].adc_sums[0], telid)

        image = disp.image.copy()

        disp.set_limits_percent(70)
        plt.pause(0.1)

        # apply really stupid image cleaning (single threshold):
        clean = image.copy()
        clean[image <= 3.0 * image.mean()] = 0.0

        # calculate image parameters
        hillas = hillas_parameters(geom.pix_x.value, geom.pix_y.value, clean)
        print(hillas)

        disp.overlay_moments(hillas, color='seagreen', linewidth=3)

        plt.show()
