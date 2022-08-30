# DATE: 18-12-21
# Abdur Rehman (202023019) ROBOTICS DEPARTMENT
# Title: HDR TONE MAPPING USING BILATERAL FILTER

# NOTE: 
# Following resources were used for the development of this code
# http://people.csail.mit.edu/fredo/PUBLI/Siggraph2002/
# https://sites.google.com/site/ianschillebeeckx/cse555/hmwk1

import os 
import cv2 as cv
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import matplotlib.pyplot as plt
import math

# Loading exposure images into a list
img_fn = ["./set3images/"+name for name in sorted(os.listdir("./set3images"))]
img_list = [cv.imread(fn) for fn in img_fn]
exposure=[]

###### Finding exposure time of all images ######
for name in sorted(os.listdir("./set3images")):
    img_dir = "./set3images/"+name
    image = Image.open(img_dir)
    exifdata = image.getexif()
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        # decode bytes 
        if isinstance(data, bytes):
            data = data.decode()
        # print(f"{tag:22}: {data}")
        if tag =="ExposureTime":
            expo = data[0]/data[1]
            # print(name, data, expo)
            exposure.append(expo)
            break
exposure_times = np.array(exposure, dtype=np.float32)


# Merge exposures to HDR image
merge_robertson = cv.createMergeRobertson()
hdr_robertson = merge_robertson.process(img_list, times=exposure_times.copy())

fig, axs = plt.subplots(1, constrained_layout=True) 
fig.suptitle('HDR Merge ROBERTSON', fontsize=16)
axs.imshow(hdr_robertson)

###### Converting HDR image to YUV color space ######
lum_coeff = [20/61, 40/61, 1/61]
in_lum = lum_coeff[0]*hdr_robertson[:,:,0] + lum_coeff[1]*hdr_robertson[:,:,2] + lum_coeff[2]*hdr_robertson[:,:,2]
tile = np.tile(in_lum,[3,1,1])
tile = np.transpose(tile,(1,2,0))
in_chrom = hdr_robertson/tile

fig, axs = plt.subplots(1, 2, constrained_layout=True) 
fig.suptitle('Luminance - Chrominance Color Space', fontsize=16)
axs[0].imshow(in_lum)
axs[0].set_title('Intensity')
axs[1].imshow(in_chrom)
axs[1].set_title('Color')  

###### Application of Bilateral Filter on HDR Image ######
log_lum = np.log10(in_lum)
base = cv.bilateralFilter(log_lum,9,75,75)
detail = log_lum - base

fig, axs = plt.subplots(1, 2, constrained_layout=True) 
fig.suptitle('Bilateral Filter', fontsize=16)
axs[0].imshow(base)
axs[0].set_title('Large scale feature')
axs[1].imshow(detail)
axs[1].set_title('Small scale feature') 

###### TONE MAPPING as described by the PAPER ######
compression_factor = np.log10(5)/(base.max()-base.min())
log_abs_scale = base.max()*compression_factor
out_log_lum = base*compression_factor + detail - log_abs_scale 
out_lum = np.power(10,out_log_lum)
tile2 = np.tile(out_lum, [3,1,1])
tile2 = np.transpose(tile2,(1,2,0))
out_img = in_chrom*tile2

fig, axs = plt.subplots(1, constrained_layout=True) 
fig.suptitle('HDR Tone Mapped Image', fontsize=16)
axs.imshow(out_img)
plt.show()

