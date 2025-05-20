from app_for_tmp_joycaption import get_prompt_by_img_path

'''2025-3-20
主要任务：
    获取图片的prompt
    并且把  model_prompt clo_prompt 
            model_path clo_path
            clo_type
    编写在json文件中
'''

import os
from os.path import join as osj
from os.path import exists as is_path_exists
import json
from tqdm import tqdm

sub_dir = 'test'

img_dir = f'/root/datasets/VITON-HD_ori/{sub_dir}/'
model_dir = osj(img_dir,'image')
cloth_dir = osj(img_dir,'cloth')
json_model_prefix = f'{sub_dir}/image'
json_clo_prefix = f'{sub_dir}/cloth'
'''
[{"text": [ a taants stands against a blue wall."], 
 "cloth_text": [ a taants stands against a blue wall."], 
    "image_file": "IGPair/images/image_000000_00.jpg", 
    "cloth_file": "IGPair/clothes/cloth_000000.jpg", 
    "cloth_type": "upper_body"}, 
'''
json_data = []
save_json_path = osj(img_dir,f'{sub_dir}.json')

for name in tqdm(os.listdir(model_dir)):
    model_path = osj(model_dir,name)
    n,_ = os.path.splitext(name)
    if is_path_exists( osj(cloth_dir,n+'.jpg') ):
        cloth_path = osj(cloth_dir,n+'.jpg')
        clo_name = n+'.jpg'
    elif is_path_exists( osj(cloth_dir,n+'.png') ):
        cloth_path = osj(cloth_dir,n+'.png')
        clo_name = n+'.png'
    elif is_path_exists( osj(cloth_dir,n+'.bmp') ):
        cloth_path = osj(cloth_dir,n+'.bmp')
        clo_name = n+'.bmp'
    else: continue
    
    model_prompt = get_prompt_by_img_path(model_path)
    cloth_prompt = get_prompt_by_img_path(cloth_path)
    
    json_dict = {}  
    json_dict['text'] = model_prompt
    json_dict['cloth_text'] = cloth_prompt
    json_dict['image_file'] = osj(json_model_prefix,name)
    json_dict['cloth_file'] = osj(json_clo_prefix,clo_name)
    json_dict['cloth_type'] = "upper_body"
    
    json_data.append(json_dict)
    # break
    
with open(save_json_path,'w') as f:
    json.dump(json_data,f)