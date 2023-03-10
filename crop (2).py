import pandas as pd
from osgeo import gdal

df = pd.read_excel('overlaps.xlsx')
N = len(df)

for row in range(N):
    lr_file = df.iloc[row, 2] + '.tif'
    hr_file = df.iloc[row, 3] + '.tif'
    bottom_right_lat, bottom_right_long = df.iloc[row, 4].lstrip('POLYGON ((').split()
    top_left_lat, top_left_long = df.iloc[row, 6].split()
    
    window = (float(top_left_lat), float(top_left_long), float(bottom_right_lat), float(bottom_right_long))
    print(window)
    gdal.Translate('cropped_' + lr_file, lr_file, projWin=window)
    gdal.Translate('cropped_' + hr_file, hr_file, projWin=window)