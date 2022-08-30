import os 
import cv2 as cv
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
# Loading exposure images into a list
# img_fn = [r"C:\Users\felipe.cunha\Documents\venv\HDRTest\100.jpg", r"C:\Users\felipe.cunha\Documents\venv\HDRTest\250.jpg", r"C:\Users\felipe.cunha\Documents\venv\HDRTest\500.jpg"]
img_fn = ["./set3images/"+name for name in sorted(os.listdir("./set3images"))]
img_list = [cv.imread(fn) for fn in img_fn]

exposure=[]

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
            print(name, data, expo)
            exposure.append(expo)
            break
exposure_times = np.array(exposure, dtype=np.float32)
# print(exposure_times)

# exposure_times = np.array([100, 250, 500], dtype=np.float32)
# Merge exposures to HDR image
merge_debevec = cv.createMergeDebevec()
hdr_debevec = merge_debevec.process(img_list, times=exposure_times.copy())
merge_robertson = cv.createMergeRobertson()
hdr_robertson = merge_robertson.process(img_list, times=exposure_times.copy())

# Tonemap HDR image
tonemap1 = cv.createTonemap(gamma=2.2)
res_debevec = tonemap1.process(hdr_debevec.copy())

tonemap2 = cv.createTonemap(gamma=2.2)
res_robert = tonemap2.process(hdr_robertson.copy())

# Exposure fusion using Mertens
merge_mertens = cv.createMergeMertens()
res_mertens = merge_mertens.process(img_list)
# Convert datatype to 8-bit and save
res_debevec_8bit = np.clip(res_debevec*255, 0, 255).astype('uint8')
res_robertson_8bit = np.clip(res_robert*255, 0, 255).astype('uint8')
res_mertens_8bit = np.clip(res_mertens*255, 0, 255).astype('uint8')
cv.imwrite("ldr_debevec.jpg", res_debevec_8bit)
cv.imwrite("ldr_robertson.jpg", res_robertson_8bit)
cv.imwrite("fusion_mertens.jpg", res_mertens_8bit)
