import torch
import os
import cv2
# from yolo.utils.utils import *
from library_dir.fashion_cutting.yolo.utils.utils import *
# from predictors.YOLOv3 import YOLOv3Predictor
from library_dir.fashion_cutting.predictors.YOLOv3 import YOLOv3Predictor
import glob
from tqdm import tqdm
import sys
from PIL import Image
# from helpers.ImageLoader import load_images_from_folder
from library_dir.fashion_cutting.helpers.ImageLoader import load_images_from_folder

# 画像リサイズ用
def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result

class detect_class:
    def detect_wear(self,pass_):

        tops_list = {
            "short sleeve top":"s_sleeve",
            "long sleeve top":"l_sleeve",
            "short sleeve outwear":"s_output",
            "long sleeve outwear":"l_output",
            "vest":"vest",
            "sling":"sling"
            }

        bottoms_list = {
            "shorts":"shorts",
            "trousers":"trousers",
            "skirt":"skirt"
        }
        dress = {
            "short sleeve dress":"s_sleeve_dress",
            "long sleeve dress":"l_sleeve_dress",
            "vest dress":"vest_dress",
            "sling dress":"sling_dress"
        }

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        torch.cuda.empty_cache()

        # user_input = input("Please enter the name of the folder of images to crop: ")

        #YOLO PARAMS
        yolo_df2_params = {"model_def" : "./library_dir/fashion_cutting/yolov3-df2.cfg",
        "weights_path" : "./library_dir/fashion_cutting/yolov3-df2_15000.weights",
        "class_path":"./library_dir/fashion_cutting/df2.names",
        "conf_thres" : 0.5,
        "nms_thres" :0.6,
        "img_size" : 416,
        "device" : device}


        #DATASET
        dataset = 'df2'

        yolo_params = yolo_df2_params




        #Classes
        classes = load_classes(yolo_params["class_path"])

        detectron = YOLOv3Predictor(params=yolo_params)


        images, filenames = load_images_from_folder(pass_)
        detections = []
        upper_counter = 0
        under_counter = 0
        # dress_counter = 0
        for i in range (len(images)):
            detections.append(detectron.get_detections(images[i]))
            
            for x1, y1, x2, y2, cls_conf, cls_pred in detections[i]:
                        
                        
                # if(classes[int(cls_pred)]=="short sleeve top" or classes[int(cls_pred)]=="long sleeve top"):
                if classes[int(cls_pred)] in list(tops_list.keys()):
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    y1 = 0 if y1<0 else y1
                
                    new_img=images[i][y1:y2,x1-5:x2+20]
                    if(new_img.any()):    
                        new_image = cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB)
                        new_image = Image.fromarray(new_image)
                        output_resize = expand2square(new_image, (125, 125, 125)).resize((500, 500))
                        output_resize.save("./static/images/output_image/tops_box/tops_"+str(upper_counter)+'.png')
                        # cv2.imwrite('./images/output_image/tops_box/tops_'+str(upper_counter)+'.png', new_img)
                        upper_counter += 1  
                        # img_id = path.split('/')[-1].split('.')[0]
                elif classes[int(cls_pred)] in list(bottoms_list.keys()):
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    y1 = 0 if y1<0 else y1
                    
                    new_img=images[i][y1:y2,x1:x2]
                    if(new_img.any()): 
                        new_image = cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB)  
                        new_image = Image.fromarray(new_image)
                        output_resize = expand2square(new_image, (125, 125, 125)).resize((500, 500)) 
                        output_resize.save("./static/images/output_image/bottoms_box/bottoms_"+str(under_counter)+'.png')
                        # cv2.imwrite('./images/output_image/bottoms_box/bottoms_'+str(under_counter)+'.png', new_img)  
                        under_counter += 1       
                        # img_id = path.split('/')[-1].split('.')[0]
                
                    
            os.remove(pass_+"/"+filenames[0])            

                
     