import cv2
import numpy as np

def deskew(im, max_skew=10):
    
    im = np.array(im.convert('RGB'))
    height, width = im.shape[:2]
    im_gs = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    im_gs = cv2.fastNlMeansDenoising(im_gs, h=3)
    im_bw = cv2.threshold(im_gs, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    lines = cv2.HoughLinesP(
        im_bw, 1, np.pi / 180, 200, minLineLength=width / 12, maxLineGap=width / 150
    )
    angles = []

    for line in lines:
        x1, y1, x2, y2 = line[0]  
        angles.append(np.arctan2(y2 - y1, x2 - x1)) 
    landscape = np.sum([abs(angle) > np.pi / 4 for angle in angles]) > len(angles) / 2  
    if landscape:
        angles = [
            angle
            for angle in angles 
            if np.deg2rad(90 - max_skew) < abs(angle) < np.deg2rad(90 + max_skew) # lọc góc 
        ]
    else:
        angles = [angle for angle in angles if abs(angle) < np.deg2rad(max_skew)]
    if len(angles) < 5:
        return im
    angle_deg = np.rad2deg(np.median(angles))
    if landscape:  
        if angle_deg < 0:
            im = cv2.rotate(im, cv2.ROTATE_90_CLOCKWISE)
            angle_deg += 90
        elif angle_deg > 0:
            im = cv2.rotate(im, cv2.ROTATE_90_COUNTERCLOCKWISE)  
            angle_deg -= 90
    M = cv2.getRotationMatrix2D((width / 2, height / 2), angle_deg, 1)
    im = cv2.warpAffine(im, M, (width, height), borderMode=cv2.BORDER_REPLICATE)
    return im