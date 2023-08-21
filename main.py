"""
    PRISMA LAB
    Sao Paulo State University
"""

import numpy as np
import math
from PIL import Image
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from dicom_dataset import create_dicom_dataset
from utils import config_reader
import random

#########
# GLOBALS
#########
W = 320  # 3D space width
H = 320  # 3D space height
D = 320   # 3D space depth

VOXEL_MM = 1

def plot3dModel(model_3d):

    # Get the indices of non-zero values
    indices = np.where(model_3d == 255)

    # Create a figure and a 3D axis
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the 3D surface using the indices
    ax.scatter(indices[0], indices[1], indices[2], c='r', marker='o')

    # Set labels for the axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()      

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

def createElipse(a,b, c, model_3d, model_3d_mask, configs):
    
    # The orthonormal base in np array starts at corner of np array, while we are drawing the elipse considering a base in the middle of plane. We need to adjust using offsets (translation)
    offset_x = round(W/2)
    offset_y = round(H/2)
    offset_z = round(D/2)
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
                z_v_top = round(z / VOXEL_MM)
                z_v_bottom = round(-z / VOXEL_MM)

                # translate to the model_3d basis
                x_v = x_v + offset_x
                y_v = y_v + offset_y
                z_v_top = z_v_top + offset_z
                z_v_bottom  = z_v_bottom  + offset_z

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
        
        createElipse(a, b, c, model_3d, model_3d_mask, configs)

        plano = model_3d[:, :, 160]

        print(plano.shape)
        pil_image = Image.fromarray(plano)
        output_path = "output_image.png"
        pil_image.save(output_path)

        create_dicom_dataset(model_3d, model_3d_mask, configs)

    #plot3dModel(model_3d)
  

if __name__ == '__main__':
    run()