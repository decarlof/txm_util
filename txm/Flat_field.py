import process_variables as pv
import numpy as np
from time import *

def ff_norm_on(acq_time, ff_pos):

#   exple: ff_norm_on(2, -4)

    # Pre-defined & set parameters
    ####################################################################
    sleeptime = 0.5
    wait = 100

    curr_SpleX_pos = pv.sample_x.get()  # Record the current sample position
    curr_AcqTime = curr_ccd_dwell_time.get()  # Record the current acquisition time
    pv.ccd_dwell_time.put(acq_time, wait=True, timeout=wait)  # set the flat-field the acqu. time
    pv.ccd_acquire_mode.put(0, wait=True, timeout=wait)  # CCD mode switched to fixed

    pv.ccd_EnableCallbacks(1, wait=True, timeout=wait) # Enable NDPluginProcess
    pv.sample_x.put(ff_pos, wait=True, timeout=wait) # move to flat-field position
    print '*** Move sample x to flat-field position: ', ff_pos
    pv.ccd_EnableFlatField.put(0, wait=True, timeout=wait) # disable flat-field for its acquisition
    pv.ccd_trigger.put(1, wait=True, timeout=wait) # acquisition of the flat field
    print '*** acquisition of the flat field: %.3f s', acq_time
    pv.ccd_SaveFlatField(1, wait=True, timeout=wait) # saving of the flat field
    pv.ccd_EnableFlatField.put(1, wait=True, timeout=wait) # enable the flat-field
    print '*** Flat-field enabled...'
    pv.sample_x.put(curr_SpleX_pos, wait=True, timeout=wait) # move to the former sample position
    print '*** Move sample x back to position...'
    pv.ccd_acquire_mode.put(1, wait=True, timeout=wait)  # CCD mode switched to continuous
    pv.ccd_dwell_time.put(curr_AcqTime, wait=True, timeout=wait)  # come back to the former acqu. time
    pv.ccd_trigger.put(1, wait=True, timeout=wait) # acquisition of the flat field
 
    return


def ff_norm_off():

    pv.ccd_EnableFlatField.put(0, wait=True, timeout=wait) # disable the flat-field
    print '*** Flat-field disabled...'

    return
    
