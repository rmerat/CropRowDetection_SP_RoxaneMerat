import numpy as np
import cv2
import PerImageProcessing
import MaskingProcess
import Evaluation
import random


VID = 0
SING_IMG = 1
INI_PROCESS = 0
SPEED_PROCESS = 1
FINAL_PROCESS = 2

def detection_process(images, mode, name_images, nb_row = 6, sky = 1, vp_on = 1):
    """
    input : list of img to be analyzed in rgb format
    output : not yet defined, prob data + flag set to one if analyzing went smoothly 
    """
    imgs_annotated = []
    imgs_crops_only = []
    stage = INI_PROCESS
    vp_pt = 0
    col_best_mask = None 

    for idx, img in enumerate(images):
  
            #print('VP 1 is: ', vp_pt)
            #cv2.waitKey(0)
            if stage == INI_PROCESS: #longer but needed to create initial mask of images 
                print('initial process...')
                hough_img, arr_mask, col_best_mask, vp_pt = PerImageProcessing.Initial_Process(img, idx, col_best_mask, nb_row = nb_row, sky = sky)
                if (idx == 0):
                    height_original = images[0].shape[0]
                #cv2.imshow('img hough_img: ', cv2.cvtColor(hough_img, cv2.COLOR_RGB2BGR))
                #cv2.waitKey(0)
                height, _, = arr_mask[0].shape
                stage = SPEED_PROCESS
                print('...speed process...')
            
            if stage == SPEED_PROCESS: #quick, use of ransac 
                print('img ', idx+1, 'out of', len(images))
                img = img[height_original-height:,:,:]
                arr_mask, img_annotated, vp_pt, cond_speed, img_crops_only, pts1, pts2 = PerImageProcessing.speed_process_lines(img, col_best_mask, arr_mask, vp_pt, vp_on=vp_on)
                cv2.imshow('img_annotated', img_annotated)
                cv2.waitKey(0)

                if(((idx+1)%10==0)):# and (idx!=0)):
                    cond_speed = 0
                    print('back to hough : %20')
                
                print(cond_speed)
                #cv2.imshow('img_annotated', img_annotated)

                if(cond_speed==0):
                    stage = INI_PROCESS
                #else :
                else:
                    imgs_annotated.append(img_annotated)
                    imgs_crops_only.append(img_crops_only)
                    r_acc, th_acc,threshold_acc = MaskingProcess.get_r_theta(pts1, pts2)
                    
                    vp_pt, _ = MaskingProcess.VP_detection(th_acc, r_acc, threshold_acc, stage)
                    vp_pt = np.asarray(vp_pt)
                    print('vp : ', vp_pt)
                                    
                    """if(mode ==VID): 
                        #draw VP point : 
                        cv2.circle(img_annotated, (int(vp_pt[0]),int(vp_pt[1])), 10, (255,255,255), 5)
                        cv2.imshow('vid : ', cv2.cvtColor(img_annotated, cv2.COLOR_RGB2BGR))
                        cv2.waitKey(0)
                        if cv2.waitKey(1) == ord('q'):
                            cv2.destroyAllWindows() 
                            break   
                    if(mode == SING_IMG):
                        cv2.imshow('crop only : ', img_crops_only)
                        cv2.imshow('img annotated: ', img_annotated)

                        cv2.waitKey(0)"""
            #filename = '/home/roxane/Desktop/M3_2022/Caterra_2912/Caterra/imgannotated/img_' + str(idx) + '.jpg'
            #cv2.imwrite(filename, img_annotated)

                
        """stage = FINAL_PROCESS


    
        if stage == FINAL_PROCESS : #save data and evaluate it 
            print('...processing done!')
            if(mode ==SING_IMG):
                crop_only = Evaluation.SaveData(img_crops_only, pts1, pts2)
                cop, cv, dv, v0, array_GT = Evaluation.LoadGroundTruth(name_images, img_annotated)
                score, precision = Evaluation.evaluate_results(cv, dv, v0, array_GT, nb_crop_row=nb_row)
                cv2.imshow('My Results : ', cv2.cvtColor(cop, cv2.COLOR_RGB2BGR))
                cv2.waitKey(0)
                if cv2.waitKey(1) == ord('q'):
                    cv2.destroyAllWindows()"""
    

    return 0 #return something en rapport avec le bon acheminement du process

if __name__ == "__main__":
    sky_on = 1
    mode = SING_IMG
    #first, get the name of the files we are going to analyze
    if (mode == VID):
        #distinguer entre mode video et mode single image?
        imgs_folder = '/home/roxane/Desktop/M3_2022/USB/Realsense_18-08-2022_10-46-58/'
        name_images = MaskingProcess.obtain_name_images(imgs_folder)
        sky_on = 1
        nb_row = 5
        vp_on = 1

    if (mode == SING_IMG): 
        imgs_folder = '/home/roxane/Desktop/M3_2022/Caterra/dataset_straigt_lines' #/home/roxane/Desktop/M3_2022/USB/Realsense_18-08-2022_10-46-58/' # '/home/roxane/Desktop/M3_2022/Caterra/dataset_straigt_lines' # '/home/roxane/Desktop/M3_2022/USB/Realsense_18-08-2022_10-46-58/' 
        name_images = 'crop_row_008.JPG' # 'crop_row_256.JPG' #'rgb000.jpg' # crop_row_001, crop_row_020, crop_row_053
        sky_on = 1
        nb_row = 3
        vp_on = 1

    # open and resize images for consistency --> returns img in rgb format
    images = MaskingProcess.obtain_images(name_images,imgs_folder, mode)

    # Main Detection function 
    if images is not None : 
        detection_process(images, mode, name_images, nb_row = nb_row, sky = sky_on, vp_on = vp_on)

    else : 
        print('No image')


        