#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Find rotation axis location for all datasets in a folder.
"""

from __future__ import print_function

import os
import sys
import json
import argparse
import numpy as np

import h5py
import tomopy
import dxchange

def get_dx_dims(fname, dataset):
    """
    Read array size of a specific group of Data Exchange file.
    Parameters
    ----------
    fname : str
        String defining the path of file or file name.
    dataset : str
        Path to the dataset inside hdf5 file where data is located.
    Returns
    -------
    ndarray
        Data set size.
    """

    grp = '/'.join(['exchange', dataset])

    with h5py.File(fname, "r") as f:
        try:
            data = f[grp]
        except KeyError:
            return None

        shape = data.shape

    return shape


def restricted_float(x):
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]"%(x,))
    return x
    

def tomo_stat(h5fname):
    

    # Read APS 32-BM raw data
    proj, flat, dark, theta = dxchange.read_aps_32id(h5fname)
    
    mean = flat[10,:,:].mean()
    amin = flat[10,:,:].min()
    amax = flat[10,:,:].max()
    std = flat[10,:,:].std()
    var = flat[10,:,:].var()

    return amin, amax, mean, std, var


def main(arg):

    parser = argparse.ArgumentParser()
    parser.add_argument("fname", help="directory containing multiple datasets or file name of a single dataset: /data/ or /data/sample.h5")
    parser.add_argument("nsino", nargs='?', type=restricted_float, default=0.5, help="location of the sinogram used by find center (0 top, 1 bottom): 0.5 (default 0.5)")

    args = parser.parse_args()

    # Set path to the micro-CT data to reconstruct.
    fname = args.fname
    nsino = float(args.nsino)

    if os.path.isfile(fname):       
        amin, amax, mean, std, var = tomo_stat(fname)
        print(fname, amin, amax, mean, std, var)
        
    elif os.path.isdir(fname):
        # Add a trailing slash if missing
        top = os.path.join(fname, '')
    
        # Set the file name that will store the rotation axis positions.
        jfname = top + "rotation_axis.json"
        print(os.listdir(top))
        
        h5_file_list = list(filter(lambda x: x.endswith(('.h5', '.hdf')), os.listdir(top)))

        print("Found: ", h5_file_list)
        print("Determining stats ...")
        
        dic_centers = {}
        case = {}
        i=0
        for fname in h5_file_list:
            h5fname = top + fname
            amin, amax, mean, std, var = tomo_stat(h5fname)
            case[0] =  {'file name' : fname }
            case[1] =  {'min' : amin }
            case[2] =  {'max' : amax }
            case[3] =  {'mean' : mean }
            case[4] =  {'std' : std }
            case[5] =  {'var' : var }
            print(case)
            dic_centers[i] = case
            i += 1

        # # Save json file containing the rotation axis
        # json_dump = json.dumps(dic_centers)
        # f = open(jfname,"w")
        # f.write(json_dump)
        # f.close()
        # print("Rotation axis locations save in: ", jfname)
    
    else:
        print("Directory or File Name does not exist: ", fname)

if __name__ == "__main__":
    main(sys.argv[1:])

