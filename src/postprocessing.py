import os
from glob import glob
from PIL import Image
import subprocess
import cv2
import numpy as np
from transparent_background import Remover
import imageio
import matplotlib.pyplot as plt
from functools import reduce 

def post_processing():

    ###GIF to PNG

    ###배경 제거 전 gif 파일 경로
    output_path = os.path.realpath('../output')
    if glob('../output/*.gif') != None:
        last_gif = glob('../output/*.gif')[-1]
    else: 
        print('No gif in directory!!')
            
    gif_filename = last_gif.split('\\')[1]
    gif_path = os.path.join(output_path,gif_filename)
    pre_rm_bg_png_folder_directory= os.path.join(output_path, 'pre_rm_bg', gif_filename[:-4])
    pre_rm_bg_png_folder = os.makedirs(pre_rm_bg_png_folder_directory, exist_ok= True)
    rm_bg_png_white_folder_directory = os.path.join(output_path, 'rm_bg_white', gif_filename[:-4])
    rm_bg_png_white_folder = os.makedirs(rm_bg_png_white_folder_directory, exist_ok= True)


    # 애니메이션 GIF 파일 열기
    image = Image.open(gif_path)
    print(gif_path)

    # 프레임 추출
    frames = []
    try:
        while True:
            frames.append(image.copy())
            image.seek(len(frames))  # 다음 프레임으로 이동
    except EOFError:
        pass

    # 각 프레임 저장
    for index, frame in enumerate(frames):
        save_file = pre_rm_bg_png_folder_directory + '/' + f"frame_"+(str(index)).zfill(5)+".png"
        frame.save(save_file, format="PNG")


    ## 배경 제거

    # Load model
    remover = Remover() # default setting
    # remover = Remover(mode='fast', device='cuda:0') # custom setting
    # remover = Remover(mode='base-nightly') # nightly release checkpoint
    # Usage for image
    img_list = glob(pre_rm_bg_png_folder_directory+'/*.png')
    rm_bg_png_output_directory = output_path+'/rm_bg_png/'+ gif_filename[:-4]
    rm_bg_png_white_output_directory = output_path+'/rm_bg_white/'+ gif_filename[:-4]
    os.makedirs(rm_bg_png_output_directory, exist_ok=True)
    os.makedirs(rm_bg_png_white_output_directory, exist_ok=True)


    for i in img_list:

        img = Image.open(i).convert('RGB') # read image
        # img = cv2.imread(i,-1)
        name = i.split('\\')[-1]
        out = remover.process(img,type='rgba') # default setting - transparent background
        white = remover.process(img,type='[255,255,255]')
        
    ##remove 옵션

    # out = remover.process(img, type='rgba') # same as above
    # out = remover.process(img, type='map') # object map only
    # out = remover.process(img, type='green') # image matting - green screen
    # out = remover.process(img, type='white') # change backround with white color

    # out = remover.process(img, threshold=0.5) # use threhold parameter for hard prediction.

        out.save(rm_bg_png_output_directory+'/'+name) # save result
        white.save(rm_bg_png_white_output_directory+'/'+name)
        

    rm_bg_gif_path = os.path.join(output_path,'rm_bg_gif')
    os.makedirs(rm_bg_gif_path, exist_ok=True)
    rm_bg_gif_directory = os.path.join(rm_bg_gif_path,gif_filename) ## 배경 제거한 gif Output 저장할 경로
    image_dir = rm_bg_png_white_output_directory ###Image Path 배경 제거된 png 파일 경로




    gif_config = {'loop': 0, 'duration':0.05}

    images = []
    for x in glob(image_dir+'/*.png'):
        img = cv2.imread(x, -1)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        # img = plt.imread(x,1)
        images.append(img)


        
    # images = [plt.imread(os.path.join(image_dir,x)) for x in os.listdir(image_dir) if x.endswith('.png')]
    # images = []
    # for x in os.listdir(image_dir):
    #     img = plt.imread(os.path.join(image_dir,x))#     images.append(img)

    imageio.mimwrite(rm_bg_gif_directory, images, format = 'GIF-PIL', **gif_config) ##file name



    ## 스프라이트 시트 만들기
    png_list = glob(rm_bg_png_output_directory+'/*.png')
    sprite_output = os.path.join(output_path,'spritesheet')
    os.makedirs(sprite_output,exist_ok=True)
    sprite_name = os.path.join(output_path,'spritesheet', gif_filename[:-4]+'.png')




    def hstack_img(x,y):
        y = cv2.imread(y,-1)
        y = cv2.cvtColor(y, cv2.COLOR_BGRA2RGBA)
        y = cv2.resize(y,(64,64))
        tmp = np.hstack([x,y])
        return tmp

    def hstack_zeros(x,y):
        y = np.zeros((64,64,4), dtype='uint8')
        tmp = np.hstack([x,y])
        
        return tmp

    def vstack_img(x,y):
        tmp = np.vstack([x,y])
        return tmp


    stack_list = []


    if len(png_list)%8 ==0:

        for i in range(len(png_list)//8):
            globals()['tmp{}'.format(i)] = []
            chunked_list = png_list[8*i:8*(i+1)]
            for j in chunked_list:
                globals()['tmp{}'.format(i)].append(j)
            
            globals()['stack{}'.format(i)] = reduce(hstack_img, chunked_list, np.zeros((64,64,4),dtype='uint8'))

            stack_list.append(globals()['stack{}'.format(i)])

        stacked_img = reduce(vstack_img, stack_list, np.zeros_like(stack_list[0], dtype='uint8'))
        stacked_img = stacked_img[:,64:] ## 맨 앞 np.zeros 제외

        cv2.imwrite(sprite_name, cv2.cvtColor(stacked_img, cv2.COLOR_BGRA2RGBA))

    elif len(png_list)>8: 

        for i in range(len(png_list)//8):
            globals()['tmp{}'.format(i)] = []
            chunked_list = png_list[8*i:8*(i+1)]
            for j in chunked_list:
                globals()['tmp{}'.format(i)].append(j)
            
            globals()['stack{}'.format(i)] = reduce(hstack_img, chunked_list, np.zeros((64,64,4),dtype='uint8'))

            stack_list.append(globals()['stack{}'.format(i)])

        stacked_img = reduce(vstack_img, stack_list, np.zeros_like(stack_list[0], dtype='uint8'))
        stacked_img = stacked_img[:,64:] ## 맨 앞 np.zeros 제외


        mod_list = []
        mod = len(png_list)%8
        for i in range(mod,0,-1):
            mod_list.append(png_list[-i])
            mod_list = sorted(mod_list)

        
        mod_stacked_img = reduce(hstack_img, mod_list, np.zeros((64,64,4), dtype='uint8') )
        zero_stacked_img = reduce(hstack_zeros, [i for i in range(8-mod)], mod_stacked_img )
        zero_stacked_img = zero_stacked_img[:,64:]
        full_stacked_img = np.vstack([stacked_img, zero_stacked_img])


        cv2.imwrite(sprite_name, cv2.cvtColor(full_stacked_img, cv2.COLOR_BGRA2RGBA))

    elif len(png_list)<8:

        mod_list = []
        mod = len(png_list)%8
        chunked_list = png_list[:mod]
        for i in range(0,mod,1):
            mod_list.append(png_list[i])
            
        for i in range(len(png_list)//8):
            globals()['tmp{}'.format(i)] = []

            for j in chunked_list:
                globals()['tmp{}'.format(i)].append(j)

        mod_stacked_img = reduce(hstack_img, chunked_list, np.zeros((64,64,4), dtype='uint8') )

        
        cv2.imwrite(sprite_name, cv2.cvtColor(mod_stacked_img, cv2.COLOR_BGRA2RGBA))

post_processing()
print('done')

