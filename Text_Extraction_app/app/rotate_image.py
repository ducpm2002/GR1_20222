import cv2
import numpy as np
import math
import re
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
import sys
sys.path.append('C:\\Users\\Duc.PM205068\\PycharmProjects\\Text_Extraction_app_test\\app')

def get_median_angle(image):
    # applying morphological transformations on the binarised image
    # to eliminate maximum noise and obtain text ares only 
    erode_otsu = cv2.erode(image,np.ones((7,7),np.uint8),iterations=1)
    negated_erode = ~erode_otsu
    opening = cv2.morphologyEx(negated_erode,cv2.MORPH_OPEN,np.ones((5,5),np.uint8),iterations=2)
    double_opening = cv2.morphologyEx(opening,cv2.MORPH_OPEN,np.ones((3,3),np.uint8),iterations=5)
    double_opening_dilated_3x3 = cv2.dilate(double_opening,np.ones((3,3),np.uint8),iterations=4)

    # finding the contours in the morphologically transformed image
    contours_otsu,_ = cv2.findContours(double_opening_dilated_3x3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    # iniatialising the empty angles list to collet the angles of each contour
    angles = []

    # obtaining the angles of each contour using a for loop
    for cnt in range(len(contours_otsu)):
        # the last output of the cv2.minAreaRect() is the orientation of the contour
        rect = cv2.minAreaRect(contours_otsu[cnt])

        # appending the angle to the angles-list
        angles.append(rect[-1])
        
    # finding the median of the collected angles
    angles.sort()
    median_angle = np.median(angles)

    # returning the median angle
    return median_angle

# funtion to correct the median-angle to give it to the cv2.warpaffine() function
def corrected_angle(angle):
        if  angle < -45 :
            corrected_angle = -(angle + 90)
        else : 
            corrected_angle = - angle      
        return corrected_angle
# function to rotate the image
def rotate_image(image: np.ndarray,angle, background_color): 
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)  
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background_color)

def get_otsu(image):
    # binarizing the image using otsu's binarization method
    _, otsu = cv2.threshold(image,180,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return otsu


def correct_skew(image):
    # getting the binarized image
    image = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    otsu = get_otsu(gray)

    median_angle = get_median_angle(otsu)
    rotated_image = rotate_image(image,corrected_angle(median_angle),(255,255,255))


    while True:

        rotated_image_gray = cv2.cvtColor(rotated_image,cv2.COLOR_BGR2GRAY)
        otsu = get_otsu(rotated_image_gray)
        osd_rotated_image = pytesseract.image_to_osd(otsu)


        angle_rotated_image = re.search('(?<=Rotate: )\d+', osd_rotated_image).group(0)

        if (angle_rotated_image == '0'):

            rotated_image = rotated_image

            break
        elif (angle_rotated_image == '90'):
            rotated_image = rotate_image(rotated_image,90,(255,255,255))
            continue
        elif (angle_rotated_image == '180'):
            rotated_image = rotate_image(rotated_image,180,(255,255,255))
            continue
        elif (angle_rotated_image == '270'):
            rotated_image = rotate_image(rotated_image,90,(255,255,255))
            continue    
    return rotated_image