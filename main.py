"""
    PRISMA LAB
    Sao Paulo State University (UNESP) - Brazil
"""

import numpy as np
import math
from PIL import Image
from mpl_toolkits.mplot3d import Axes3D
from dicom_dataset import create_dicom_dataset
from utils import config_reader
import random
import sys
import projection
from utils.plot import plot3dModel
import string

#########
# GLOBALS
#########
W = 150  # 3D space width
H = 150  # 3D space height
D = 150   # 3D space depth

VOXEL_MM = 1

# y = f(x)
# x = mm unit
# return y, in mm
# return None if x is out of elipse domain
def elipseEquation(x, a, b):
    aux = (1 - (((x)**2)/(a**2)))*(b**2)
    print(x)
    print(aux)
    if aux < 0:
        return None
    return math.sqrt(aux)

# z = f(x, y)
# x, y = mm unit
# return z, in mm
# return None if x is out of elipse domain
def elipseEquation3d(x, y, a, b, c):
    aux = (1 - ((x**2)/(a**2))-((y**2)/(b**2)))*(c**2)
    if aux < 0:
        return None
    return math.sqrt(aux)

def createElipse(a,b, c, model_3d, model_3d_mask, image_array_attenuation, configs):
    
    # The orthonormal base in np array starts at corner of np array, while we are drawing the elipse considering a base in the middle of plane. We need to adjust using offsets (translation)
    offset_x = round(W/2)
    offset_y = round(H/2)
    offset_z = round(D)
    thicknedd_egg_shell = int(configs["General"]["THICKNESS_EGG_SHELL_INTERVAL"])
    # Define a random egg shell thickness for this samples
    random_thickness = random.randint(0, thicknedd_egg_shell)

    for i in range(random_thickness):
        # We draw several elipses increasing their radius to simulate the egg shell thickness
        a += 1
        b += 1
        for x in np.linspace((-a), a, 500):
            for y in np.linspace((-b), b, 500):

                z = elipseEquation3d(x, y, a, b, c) # return z in mm
                if z is None:   # if x is out of elipse domain, continue
                    continue

                # transform mm to voxels qtd
                x_v = round(x / VOXEL_MM)
                y_v = round(y/VOXEL_MM)
                z_v_top = round(z / VOXEL_MM) + round(c)
                z_v_bottom = round(-z / VOXEL_MM) + round(c)

                # translate to the model_3d basis
                x_v = x_v + offset_x -1
                y_v = y_v + offset_y -1
                z_v_top = offset_z - z_v_top -1
                z_v_bottom  = offset_z - z_v_bottom -1# + offset_z 

                #print(z)
                ## Interpolate mm -> voxel
                # + offset_x
                # + offset_z
                # + offset_z
                #print("x: "+str(x_v) + "y: "+ str(y_v)+" z: " + str(z_v_top) + " z_bottom: " + str(z_v_bottom))
                # Set the 

                model_3d[z_v_top, x_v, y_v] = 255
                model_3d[z_v_bottom, x_v, y_v ] = 255

                model_3d_mask[z_v_top, x_v, y_v] = 1
                model_3d_mask[z_v_bottom, x_v, y_v ] = 1

                image_array_attenuation[z_v_top, x_v, y_v] = 0.01
                image_array_attenuation[z_v_bottom, x_v, y_v] = 0.01


def run():

    NUM_SAMPLES = 100
    print("Creating "+str(NUM_SAMPLES) + " samples.")
    # Read ini config 
    configs = config_reader.read_config("config.ini")

    for i in range(NUM_SAMPLES):
        print("Creating " +str(i+1) + "-th sample...")
        # Create the 3D model filled with zeros
        model_3d = np.zeros((W, H, D), dtype=np.uint8)
        model_3d_mask = np.zeros((W, H, D), dtype=np.uint8)
        image_array_attenuation = np.zeros((W, H, D), dtype=np.float16)

        # Define a random egg size from confif file
        a_min = int(configs["General"]["A_MIN"])
        a_max = int(configs["General"]["A_MAX"])
        b_min = int(configs["General"]["B_MIN"])
        b_max = int(configs["General"]["B_MAX"])
        c_min = int(configs["General"]["C_MIN"])
        c_max = int(configs["General"]["C_MAX"])
        a = random.randint(a_min, a_max)   # Elipse x radius in mm
        b = random.randint(b_min, b_max)   # Elipse y radius in mm
        c = random.randint(c_min, c_max)
        if a > W*VOXEL_MM or b > H*VOXEL_MM:
            print("It is not generate a egg greater than the 3d image")
            raise(ValueError)
        
        # TODO: Verify if the egg dimension summed with the greatest thichness could extrapolate the 3d volum. If yes, raise an exception
        createElipse(a, b, c, model_3d, model_3d_mask, image_array_attenuation, configs)

        #plot3dModel(model_3d)

        #plano = model_3d[:, :, 160]

        #print(plano.shape)
        #pil_image = Image.fromarray(plano)
        #output_path = "output_image.png"
        #pil_image.save(output_path)


        # Generates a random name to the model
        
        name_lenght = 10
        characters = string.ascii_lowercase + string.digits
        random_name = ''.join(random.choice(characters) for _ in range(name_lenght))

        projection.project_blue_box(random_name, model_3d, image_array_attenuation, configs, VOXEL_MM, W, H, D)
        create_dicom_dataset(random_name, model_3d, model_3d_mask, configs)

    #plot3dModel(model_3d)
  

if __name__ == '__main__':
    run()