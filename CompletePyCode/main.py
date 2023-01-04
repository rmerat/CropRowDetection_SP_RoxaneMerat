import numpy as np
import cv2
import PerImageProcessing
import MaskingProcess
import Evaluation


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

    for idx, img in enumerate(images):
        #print(idx, 'stage : ', stage)
        if stage == INI_PROCESS: #longer but needed to create initial mask of images 
            print('initial process...')
            hough_img, arr_mask, col_best_mask, vp_pt = PerImageProcessing.Initial_Process(img, nb_row = nb_row, sky = sky)
            height_original = images[0].shape[0]
            height, _, = arr_mask[0].shape
            stage = SPEED_PROCESS
            print('...speed process...')
        
        if stage == SPEED_PROCESS: #quick, use of ransac 

            img = img[height_original-height:,:,:]
            arr_mask, img_annotated, vp_pt, cond_speed, img_crops_only, pts1, pts2 = PerImageProcessing.speed_process_lines(img, col_best_mask, arr_mask, vp_pt, vp_on=vp_on)
            
            if(cond_speed==0):
                print('back to ini!')
                stage = INI_PROCESS
            else :
                imgs_annotated.append(img_annotated)
                imgs_crops_only.append(img_crops_only)
            
                if(mode ==VID): 
                    cv2.imshow('vid :q ', cv2.cvtColor(img_annotated, cv2.COLOR_RGB2BGR))
                    if cv2.waitKey(1) == ord('q'):
                        cv2.destroyAllWindows() 
                        break   
                if(mode == SING_IMG):
                    cv2.imshow('crop only : ', img_crops_only)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
            
    print('point describing crop before evaluation : ', pts1, pts2)
    stage = FINAL_PROCESS

    if stage == FINAL_PROCESS : #save data and evaluate it 
        print('...processing done!')
        if(mode ==SING_IMG):
            crop_only = Evaluation.SaveData(img_crops_only, pts1, pts2)
            cop, cv, dv, v0 = Evaluation.LoadGroundTruth(name_images)
            score, precision = Evaluation.evaluate_results(cv, dv, v0)

            cv2.imshow('img : ', cv2.cvtColor(img_annotated, cv2.COLOR_RGB2BGR))
            cv2.imshow('crop_only', crop_only)
            cv2.waitKey(0)
            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()

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
        vp_on = 0


    if (mode == SING_IMG): 
        print('sing img')
        imgs_folder = '/home/roxane/Desktop/M3_2022/Caterra/dataset_straigt_lines'
        name_images = 'crop_row_023.JPG' #crop_row_001, crop_row_020, crop_row_053
        #imgs_folder = '/home/roxane/Desktop/M3_2022/crop_dataset/'
        #name_images = 'crop_row_001.JPG'
        sky_on = 0
        nb_row = 4
        vp_on = 1


    #open and resize images for consistency --> returns img in rgb format
    images = MaskingProcess.obtain_images(name_images,imgs_folder, mode)
    print(images[0].shape)

    # Main Detection function 
    if images is not None : 
        detection_process(images, mode, name_images, nb_row = nb_row, sky = sky_on, vp_on = vp_on)

    else : 
        print('No image')


        