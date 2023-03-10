import json
import os,sys
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
from shapely.geometry import Point, Polygon
from xml.dom import minidom
from datetime import datetime

def getCoordinates(filename):
	final_coord = []
	tree =  minidom.parse(filename)
	final_coord.append([float(tree.getElementsByTagName("isda:upper_left_longitude")[1].firstChild.nodeValue), float(tree.getElementsByTagName("isda:upper_left_latitude")[1].firstChild.nodeValue)])
	final_coord.append([float(tree.getElementsByTagName("isda:lower_left_longitude")[1].firstChild.nodeValue), float(tree.getElementsByTagName("isda:lower_left_latitude")[1].firstChild.nodeValue)])
	final_coord.append([float(tree.getElementsByTagName("isda:lower_right_longitude")[1].firstChild.nodeValue), float(tree.getElementsByTagName("isda:lower_right_latitude")[1].firstChild.nodeValue)])
	final_coord.append([float(tree.getElementsByTagName("isda:upper_right_longitude")[1].firstChild.nodeValue), float(tree.getElementsByTagName("isda:upper_right_latitude")[1].firstChild.nodeValue)])
	return final_coord

def cropImage(filename, img_coord, overlap_coord):
	print(filename)
	img = np.array(Image.open(filename))
	m, n = img.shape
	
	if my_dict.get(filename) is None:
		diff_x1 = (img_coord[3][0] - img_coord[0][0])/n
		diff_y1 = (img_coord[3][1] - img_coord[0][1])/n
		diff_x2 = (img_coord[1][0] - img_coord[0][0])/m
		diff_y2 = (img_coord[1][1] - img_coord[0][1])/m

		final = np.zeros((img.shape[0], img.shape[1], 2), dtype = np.float64)
		initial_coord = np.zeros((2, ), dtype=np.float64)
		initial_coord[0] = img_coord[0][0]
		initial_coord[1] = img_coord[0][1]
		next_coord = np.copy(initial_coord)
		for i in range(m):
			for j in range(n):
				final[i, j, 0] = next_coord[0]
				final[i, j, 1] = next_coord[1]
				next_coord[0] = next_coord[0] + diff_x1
				next_coord[1] = next_coord[1] + diff_y1
			initial_coord[0] = initial_coord[0] + diff_x2
			initial_coord[1] = initial_coord[1] + diff_y2
			next_coord = np.copy(initial_coord)
		my_dict[filename] = final
	else:
		final = my_dict.get(filename)
	#print(final)
	
	overlap_area = Polygon(overlap_coord)

	cropped_img = np.copy(img)
	for i in range(m):
		for j in range(n):
			if(overlap_area.contains(Point(final[i, j, 0], final[i, j, 1]))):
				continue
			else:
				cropped_img[i][j] = 0

	cropped_img = cropped_img[~np.all(cropped_img == 0, axis=1)]
	cropped_img = np.transpose(cropped_img)
	cropped_img = cropped_img[~np.all(cropped_img == 0, axis=1)]
	for i in range(cropped_img.shape[0]):
		for j in range(cropped_img.shape[1]):
			if cropped_img[i,0] == 0:
				cropped_img[i]=np.roll(cropped_img[i], -1)
	cropped_img = np.transpose(cropped_img)
	cropped_img = cropped_img[~np.all(cropped_img == 0, axis=1)]
	#print(cropped_img)
	return cropped_img

if(Path('Dictionary.txt').is_file()):
	with open('dictionary.txt') as f:
		data = f.read()
	my_dict = json.loads(data)
else:
	my_dict = {}

with open("overlaps.csv") as fread:
	lines = fread.readlines()

for line in lines:
	line_splits = line.split(';')
	lr_foldername = line_splits[0]
	lr_filename = line_splits[2]
	hr_folder_name = line_splits[1]
	hr_filename = line_splits[3]
	overlap_string = line_splits[4]
	
	overlap_coord_string = overlap_string.split('POLYGON ((')[1].split('))')[0]
	overlap_coord_list = overlap_coord_string.split(', ')
	overlap_coord = []
	for element in overlap_coord_list:
		overlap_coord.append(tuple([float(element.split(' ')[0]), float(element.split(' ')[1])]))
	
	lr_dir = "lr/"+lr_filename.split('_')[1]+"_"+lr_filename.split('_')[2]+"/"+lr_filename
	lr_xml_list = [file for file in os.listdir(lr_dir) if file.endswith('.xml')]
	lr_xml_file = lr_xml_list[0]
	lr_img_coord = getCoordinates(os.path.join(lr_dir, lr_xml_file))
	lr_img_file = os.path.join(lr_dir, [file for file in os.listdir(lr_dir) if file.endswith('.png')][0])
	
	hr_dir = "hr/"+hr_filename.split('_')[1]+"_"+hr_filename.split('_')[2]+"/"+hr_filename
	hr_xml_file = [file for file in os.listdir(hr_dir) if file.endswith('.xml')][0]
	hr_img_coord = getCoordinates(os.path.join(hr_dir, hr_xml_file))
	hr_img_file = os.path.join(hr_dir, [file for file in os.listdir(hr_dir) if file.endswith('.png')][0])
	
	lr_crop_filepath = "input/"+lr_filename+"_"+lr_foldername.split('.')[0]+"__"+hr_filename+"_"+hr_folder_name.split('.')[0]+".png"
	hr_crop_filepath = "output/"+lr_filename+"_"+lr_foldername.split('.')[0]+"__"+hr_filename+"_"+hr_folder_name.split('.')[0]+".png"
	
	try:
		lr_crop = cropImage(lr_img_file, lr_img_coord, overlap_coord)
		lr_crop_img = Image.fromarray(lr_crop)
		lr_crop_img.save(lr_crop_filepath)

		hr_crop = cropImage(hr_img_file, hr_img_coord, overlap_coord)
		hr_crop_img = Image.fromarray(hr_crop)
		hr_crop_img.save(hr_crop_filepath)
	except Exception:
		print("{} {}".format(lr_crop_filepath, hr_crop_filepath))

with open('Dictionary.txt', 'w') as fwrite:
     fwrite.write(json.dumps(my_dict))

'''
img = np.array(Image.open("ch2_tmc_ncf_20200203T1845562233_d_img_m65/browse/calibrated/20200203/ch2_tmc_ncf_20200203T1845562233_b_brw_m65.png"))
print(img.shape)
m, n = img.shape
final_coord = getCoordinates("ch2_tmc_ncf_20200203T1845562233_d_img_m65/data/calibrated/20200203/ch2_tmc_ncf_20200203T1845562233_d_img_m65.xml")
df = pd.read_csv('ch2_tmc_ncf_20200203T1845562233_d_img_m65/geometry/calibrated/20200203/ch2_tmc_ncf_20200203T1845562233_g_grd_m65.csv', sep = ',')

#diff_x1 = (df['Longitude'].iloc[1] - df['Longitude'].iloc[0])/100
#diff_y1 = (df['Latitude'].iloc[1] - df['Latitude'].iloc[0])/100
#diff_hor = [diff_x1, diff_y1]
#print(df.loc[df['Scan'] == 100]['Longitude'].iloc[0])
#print(df.loc[df['Scan'] == 100]['Latitude'].iloc[0])
#diff_x2 = (df.loc[df['Scan'] == 100]['Longitude'].iloc[0] - df['Longitude'].iloc[0])/100
#diff_y2 = (df.loc[df['Scan'] == 100]['Latitude'].iloc[0] - df['Latitude'].iloc[0])/100
#diff_ver = [diff_x2, diff_y2]

diff_x1 = (final_coord[3][0] - final_coord[0][0])/n
diff_y1 = (final_coord[3][1] - final_coord[0][1])/n
diff_x2 = (final_coord[1][0] - final_coord[0][0])/m
diff_y2 = (final_coord[1][1] - final_coord[0][1])/m

print("{}, {}, {}, {}\n".format(diff_x1, diff_y1, diff_x2, diff_y2))
print(final_coord)
final = np.zeros((img.shape[0], img.shape[1], 2), dtype = np.float64)
initial_coord = np.zeros((2, ), dtype=np.float64)
initial_coord[0] = final_coord[0][0]
initial_coord[1] = final_coord[0][1]
next_coord = np.copy(initial_coord)
for i in range(m):
	for j in range(n):
		final[i, j, 0] = next_coord[0]
		final[i, j, 1] = next_coord[1]
		next_coord[0] = next_coord[0] + diff_x1
		next_coord[1] = next_coord[1] + diff_y1
	initial_coord[0] = initial_coord[0] + diff_x2
	initial_coord[1] = initial_coord[1] + diff_y2
	next_coord = np.copy(initial_coord)

print(final)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

#overlapping_pol = Polygon([(25.205571822087276 - diff_hor[0], -13.778034538902265 + diff_ver[1]), (25.154024 + diff_hor[0], -13.770325 + diff_ver[1]), (25.162308 + diff_hor[0], -12.941111 - diff_ver[1]), (25.20475669149536 - diff_hor[0] , -12.947463253131659 - diff_ver[1]), (25.205571822087276 - diff_hor[0], -13.778034538902265 + diff_ver[1])])

overlapping_pol = Polygon([(25.205571822087276, -13.778034538902265), (25.154024, -13.770325), (25.162308,-12.941111), (25.20475669149536, -12.947463253131659), (25.205571822087276, -13.778034538902265)])

print(overlapping_pol)

img_cp = np.copy(img)
#print("img_cp : ", img_cp)
for i in range(m):
	for j in range(n):
		#p = Point(final[i][j][0], final[i][j][1])
		#print(p.within(overlapping_pol))
		#if(p.within(overlapping_pol)):
		if(overlapping_pol.contains(Point(final[i, j, 0], final[i, j, 1]))):
			continue
		else:
			img_cp[i][j] = 0

#final_df = pd.DataFrame(img_cp, header=None)
#final_df.drop(final_df.loc[final_df.sum(axis=1)==0].index, inplace=True)
#final_df = final_df.drop(columns=final_df.columns[final_df.sum()==0], inplace=True).to_numpy()

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

img_cp = img_cp[~np.all(img_cp == 0, axis=1)]
img_cp = np.transpose(img_cp)
img_cp = img_cp[~np.all(img_cp == 0, axis=1)]
for i in range(img_cp.shape[0]):
	for j in range(img_cp.shape[1]): # prevent infinite loop if row all zero
		if img_cp[i,0] == 0:
			img_cp[i]=np.roll(img_cp[i], -1)
img_cp = np.transpose(img_cp)
img_cp = img_cp[~np.all(img_cp == 0, axis=1)]

print(img)
print(img.shape)
print(img_cp)
print(img_cp.shape)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

i = Image.fromarray(img_cp)
i.save("image_input.png")  

#print(img.shape)
#print(final.shape)
#print(img)
#print(final)
'''

