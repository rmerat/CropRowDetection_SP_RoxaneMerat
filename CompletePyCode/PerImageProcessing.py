#Imports
import numpy as np
import matplotlib.pyplot as plt
import cv2
import extcolors
import skimage
import scipy
from PIL import Image
import math
import skimage
from sklearn.linear_model import LinearRegression
import pandas as pd
from colormap import rgb2hex
import numpy as np
import cv2
import os
import MaskingProcess



def Initial_Process(img, nb_row = 4, sky = 0):

    #Cut off sky
    if(sky==1) : 
        grad_sky = MaskingProcess.get_sky_region_gradient(img)
        img_no_sky = MaskingProcess.cut_image_from_mask(grad_sky, img)
    else : 
        img_no_sky = img

    best_mask_median, col_best_mask = MaskingProcess.veg_segmentation(img, img_no_sky)
    best_mask_median_edge = cv2.Canny(best_mask_median,100,200)

    arr_mask, th_acc, r_acc, threshold_acc, best_mask_evaluate = MaskingProcess.keep_mask_max_acc_lines(best_mask_median_edge, img_no_sky, nb_row)

    vp_pt = np.asarray(MaskingProcess.VP_detection(th_acc, r_acc, threshold_acc, best_mask_median_edge))

    #cv2.imshow('after initial process', best_mask_evaluate)
    #cv2.waitKey(0)

    arr_mask = check_equidistance(arr_mask)

    return best_mask_evaluate, arr_mask, col_best_mask, vp_pt

def Speed_Process(img, arr_mask, col_best_mask, vp_pt, nb_row = 4,  sky_on = 0):

    annotated_img = np.copy(img)
    img_lab = skimage.color.rgb2lab(img/255)

    col_best_mask_lab = skimage.color.rgb2lab((col_best_mask[0]/255, col_best_mask[1]/255, col_best_mask[2]/255))
    
    # vegetation segmentation using mask of the detected vegetal color
    best_mask = MaskingProcess.mask_vegetation(img_lab, col_best_mask_lab)
    best_mask_median = cv2.medianBlur(best_mask,3)

    #cv2.imshow('best_mask_median', best_mask_median)
    #cv2.waitKey(1000)

    #print(best_mask_median.shape)
    model = MaskingProcess.pattern_ransac(arr_mask, vp_pt, best_mask_median) 


    for crop in model:
        crop = np.asarray(crop)
        diff = (crop[1]-crop[0])
        cv2.line(annotated_img, crop[0], crop[1]+5*diff, (50,200,50), 3)


    cv2.line(annotated_img, (10,100), (100,10), (255,0,0), 10)
    cv2.line(annotated_img, (100,10), (10,100), (0,255,0), 5)
    cv2.line(annotated_img, (10,10), (100,100), (0,0,255), 2)

    return annotated_img, arr_mask

def check_equidistance(arr_mask):

    return arr_mask

def speed_process_lines(image, col_best_mask, arr_mask, vp_pt, vp_on):

    img_lab = skimage.color.rgb2lab(image/255) #calculate best color mask based on previously calculated color 
    col_best_mask_lab = skimage.color.rgb2lab((col_best_mask[0]/255, col_best_mask[1]/255, col_best_mask[2]/255))

    best_mask = MaskingProcess.mask_vegetation(img_lab, col_best_mask_lab)
    #plt.imshow(mask_col)
    band_width = int(image.shape[1]/25)
    #print('bw : ', band_width)
    # mask_col_edge = cv2.Canny(mask_col,100,200) #add la cond sur le laplacien 

    pts1 = []
    pts2 = []
    acc_m = []
    masked_images = []
    img_ransac_lines = np.copy(image)
    crops_only = np.zeros_like(image)
    #cr = np.zeros_like(best_mask)
    arr_mask_new = []

    
    for i in range(len(arr_mask)):
        masked_images.append(cv2.bitwise_and(best_mask, arr_mask[i]))
        #cv2.imshow('masked image of i :', masked_images[i])
        #cv2.waitKey(0)

    
    for i in range(len(arr_mask)): #for each row
        mask_single_crop = np.zeros_like(best_mask)
        cond = m = cond_horizon = cond_double = 0


        """
        p1 = [0, 100]
        p2 = [100, 0]
        m=0"""

        #p1, p2, m = apply_ransac(image, masked_images[i], vp_pt, 0)

        
        while(cond_horizon*cond_double == 0 ): 
            p1, p2, m, cond_speed = MaskingProcess.apply_ransac(image, masked_images[i], vp_pt, vp_on, best_mask, arr_mask[i], i) #HERE JUST CHANGED 
            
            if (cond_speed==0): 
                print('reinitialization')
                #reinitialize(img_lab, col_best_mask_lab)
                #p1, p2, m, cond_speed = MaskingProcess.apply_ransac(image, masked_images[i], vp_pt, 0, best_mask, arr_mask[i], i)
                return arr_mask_new, img_ransac_lines, vp_pt, cond_speed, crops_only

            
            masked_images[i], cond_horizon = MaskingProcess.remove_horizon(p1, p2, m, masked_images[i], band_width)
            masked_images[i], cond_double = MaskingProcess.remove_double(p1, p2, m, acc_m, masked_images[i], band_width)
            #cond_horizon, cond_double = check_ransac_cond(p1,p2,m, acc_m)
            if (cond_horizon*cond_double==0):
                print('still not met')
                #cv2.imshow('new with still bad cond : ', masked_images[i])
        
        pts1.append(p1)
        pts2.append(p2)
        acc_m.append(m)
        cv2.line(img_ransac_lines, p1, p2, (255,0,0), 1)
        cv2.line(crops_only, p1, p2, (255,0,0), 1)
        cv2.line(mask_single_crop, p1, p2, (255,0,0), band_width)
        arr_mask_new.append(mask_single_crop)

    #TODO : put back : vp_pt = intersect_multiple_lines(pts1, pts2)
    #for debugging : add drawing of VP point 

    #cv2.imshow('ransac lines : ', img_ransac_lines)
    print('point return to describe lines : ', pts1, pts2)

    return arr_mask_new, img_ransac_lines, vp_pt, 1, crops_only, pts1, pts2
