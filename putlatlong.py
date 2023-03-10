#!/usr/bin/env python3

import torch.backends.cudnn as cudnn
import torch.optim
import torch.utils.data
import torchvision.transforms as transforms
#from datasets import *
#from nltk.translate.bleu_score import corpus_bleu
import torch.nn.functional as F
from tqdm import tqdm
import argparse
import time
import argparse
import os
from pathlib import Path
#import gdal
import os
from osgeo import gdal, osr
from osgeo import osr,ogr
#import ogr
import shutil
import subprocess
import math

def calculate_rotation(top_left, top_right, bottom_left, bottom_right):
    # Create a spatial reference system for the image
    srs = osr.SpatialReference()
    srs.ImportFromProj4("+proj=longlat +a=1737400 +b=1737400 +lat_0=0 +lon_0=90")  # Selenographic coordinate system
    # Create a transform object to convert between the image's coordinate system and geographic coordinates
    transform = osr.CoordinateTransformation(srs, srs.CloneGeogCS())

    # Convert the coordinates of the image's corners to geographic coordinates
    top_left_geo = transform.TransformPoint(*top_left)[:2]
    top_right_geo = transform.TransformPoint(*top_right)[:2]
    bottom_left_geo = transform.TransformPoint(*bottom_left)[:2]
    bottom_right_geo = transform.TransformPoint(*bottom_right)[:2]

    # Calculate the angle between the top edge of the image and the North-South direction
    top_edge = (top_right_geo[0] - top_left_geo[0], top_right_geo[1] - top_left_geo[1])
    north_south = (0, 1)
    rotation_north_south = 180 / 3.14159265 * math.acos(
        sum(i * j for i, j in zip(top_edge, north_south)) / math.sqrt(
            sum(i * i for i in top_edge) * sum(i * i for i in north_south)))

    # Calculate the angle between the left edge of the image and the East-West direction
    left_edge = (bottom_left_geo[0] - top_left_geo[0], bottom_left_geo[1] - top_left_geo[1])
    east_west = (1, 0)
    rotation_east_west = 180 / 3.14159265 * math.acos(sum(i * j for i, j in zip(left_edge, east_west)) / math.sqrt(
        sum(i * i for i in left_edge) * sum(i * i for i in east_west)))
    return (rotation_east_west, rotation_north_south)

def calculate_rotationm(top_left, top_right, bottom_left, bottom_right):
    # Calculate the x-rotation
    x_rotation = math.atan2(top_right[1] - top_left[1], top_right[0] - top_left[0])
    x_rotation = math.degrees(x_rotation)
    # Calculate the y-rotation
    y_rotation = math.atan2(bottom_left[1] - top_left[1], bottom_left[0] - top_left[0])
    y_rotation = math.degrees(y_rotation)
    return x_rotation, y_rotation

def calculate_rotationg(top_left, top_right, bottom_left, bottom_right):
    # Create the transformer
    transformer = gdal.Transformer(None, None, [])

    # Set the source and destination coordinate systems
    transformer.SetSrcGeoTransform([top_left[0], 1, 0, top_left[1], 0, 1])
    transformer.SetDstGeoTransform([top_left[0], 1, 0, top_left[1], 0, 1])

    # Calculate the rotation
    success, x_rotation, y_rotation = transformer.TransformPoint(0, top_right[0], top_right[1])
    if not success:
        raise Exception("Transformation failed")
    return x_rotation, y_rotation

def calculate_geotransform(top_left, top_right, bottom_left, bottom_right,cols,rows):
    x_origin = top_left[0]
    x_pixel_size = (top_right[0] - top_left[0]) / cols
    y_origin = top_left[1]
    y_pixel_size = (bottom_left[1] - top_left[1]) / rows
    (rotation_east_west, rotation_north_south) = calculate_rotation(top_left, top_right, bottom_left, bottom_right)
    print(rotation_east_west)
    print(rotation_north_south)
    return (x_origin, x_pixel_size, rotation_east_west, y_origin, rotation_north_south, y_pixel_size)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MOON SR Data')
    parser.add_argument('--lrXMLFile', default=".\\fullImageInference\\8bitTif\\", help='OPPath8bitTifHR')
    parser.add_argument('--lrDataFile', default=".\\fullImageInference\\8bitpngTiles\\", help='OPPath8bitTifHRTilePath')
    parser.add_argument('--hrXMLFile', default=".\\fullImageInference\\8bitpngTiles\\", help='OPPath8bitTifHRTilePath')
    parser.add_argument('--hrDataFile', default=".\\fullImageInference\\8bitpngTiles\\", help='OPPath8bitTifHRTilePath')
    parser.add_argument('--CommonPortion', default="./fullImageInference/8bitpngTiles/", help='path of image dataset.')

    # flagConver16bitTifto16Tiles = True
    # flagConver16Tilesto8bit = True
    args = parser.parse_args()
    # if (os.path.exists(args.OPPath8bitTifHR)):
    #     shutil.rmtree(args.OPPath8bitTifHR)
    # if (os.path.exists(args.OPPath8bitTifHRTilePath)):
    #     shutil.rmtree(args.OPPath8bitTifHRTilePath)
    # if not (os.path.exists(args.OPPath8bitTifHR) and os.path.isdir(args.OPPath8bitTifHR)):
    #     os.makedirs(args.OPPath8bitTifHR)
    # if not (os.path.exists(args.OPPath8bitTifHRTilePath) and os.path.isdir(args.OPPath8bitTifHRTilePath)):
    #     os.makedirs(args.OPPath8bitTifHRTilePath)



    # Input file
    driver = gdal.GetDriverByName("HFA")
    infilepath = 'C:\\Users\\devesh\\Downloads\\Compressed\\ch2_ohr_ncp_20210401T2200364910_d_img_d18\\data\\calibrated\\20210401\\ch2_ohr_ncp_20210401T2200364910_d_img_d18.img'
    outfilepath = 'C:\\Users\\devesh\\Downloads\\Compressed\\ch2_ohr_ncp_20210401T2200364910_d_img_d18\\data\\calibrated\\20210401\\ch2_ohr_ncp_20210401T2200364910_d_img_d1812.tif'
    # Open the image file
    ds = gdal.Open(infilepath, gdal.GA_Update)
    # Check if the file was opened successfully
    if ds is None:
        print("Error: Could not open ENVI image file.")

    # Get the number of bands in the image
    band_count = ds.RasterCount

    # Get the image dimensions
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    x = ds.ReadAsArray()
    # Define the TIF file's geotransform and projection
    # Create an empty TIFF image
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create(outfilepath, cols, rows, 1, gdal.GDT_Byte)

    # Set the projection and geotransform of the image
    srs = osr.SpatialReference()
    srs.ImportFromProj4("+proj=longlat +a=1737400 +b=1737400 +lat_0=0 +lon_0=90")
    out_ds.SetProjection(srs.ExportToWkt())

    # Latitude and longitude of the image
    lat = -12.941111
    lon = 25.162308

    # Compute the geotransform
    x_origin = lon
    y_origin = lat
    pixel_width = 0.000001
    pixel_height = 0.000001
    out_ds.SetGeoTransform(calculate_geotransform([25.162308,-12.941111], [25.303328,-12.962214], [25.154024,-13.770325], [25.295565,-13.791494],cols,rows))
    out_ds.GetRasterBand(1).WriteArray(x)

    # Close the image file
    out_ds = None
