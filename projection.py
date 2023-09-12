import os
import numpy as np
import multiprocessing
import time
from utils.plot import plot3dModel
import matplotlib.pyplot as plt
import copy


# This function is usefull if we want VOXEL_MM different to 1mm
def extract_slices(image_array, image_array_mask, configs):
    #print(image_array[:, :].shape)
    #exit()
    slices = []
    masks = []
    # TODO: GET SLICES ONLY IN THE VOXEL_MM INTERVAL
    #TODO: THIS FUNCTION WORKS ONLY WITH VOXEL_MM = 1mm
    for i in range(image_array.shape[-1]):
        slice = image_array[:, :, i]
        mask = image_array_mask[:, :, i]
        slices.append(slice)
        masks.append(mask)
    
    return slices, masks

def receptor_plane_equation(x, y, a,b,c,d):
    if c == 0:
        c = 0.00001
    return  (d - (-a*x) - (b*y))/c

def ray(pixel_x, pixel_y, pixel_z, focus_x, focus_y, focus_z, image_array_attenuation, VOXEL_MM, final_pixel, model_3d, EMISSION_POINT):
    final_pixel = 100
    
    x0 = pixel_x
    y0 = pixel_y
    z0 = pixel_z

    PLANE_Y_POSITION = 200

    ###
    # Ray from voxel to projection plane
    ###
    for index, t in enumerate(np.linspace(0,50,4000)):
        # Parametric line equation
        x = x0 + t*(focus_x-x0)
        y = y0 + t*(focus_y-y0)
        z = z0 + t*(focus_z-z0)

        if y >= PLANE_Y_POSITION:  # Receptor plane lives on x = 75
            break

        try:
            if image_array_attenuation[round(x/VOXEL_MM), round(y/VOXEL_MM), round(z/VOXEL_MM)] == 0:
                continue
        except IndexError as e: # If t makes the actual point extrapolate the 3d volume, we return the final pixel
            break

        final_pixel -= (final_pixel * image_array_attenuation[round(x/VOXEL_MM), round(y/VOXEL_MM), round(z/VOXEL_MM)])

        ###
        # Ray from voxel to light emissor
        ###
        for index, t2 in enumerate(np.linspace(0,50,4000)):
            # Parametric line equation
            x = x0 + t2*(EMISSION_POINT[0]-x0)
            y = y0 + t2*(EMISSION_POINT[1]-y0)
            z = z0 + t2*(EMISSION_POINT[2]-z0)

            if z >= 150:  # Receptor plane lives on x = 75
                break

            try:
                if image_array_attenuation[round(x/VOXEL_MM), round(y/VOXEL_MM), round(z/VOXEL_MM)] == 0:
                    continue
            except IndexError as e: # If t makes the actual point extrapolate the 3d volume, we return the final pixel
                break

            final_pixel -= (final_pixel * image_array_attenuation[round(x/VOXEL_MM), round(y/VOXEL_MM), round(z/VOXEL_MM)])


    # Calculate the intersection between the ray with the projection plane. 
    t = (PLANE_Y_POSITION - y0)/(focus_y-y0)
    x = x0 + t*(focus_x-x0)
    z = z0 + t*(focus_z-z0)

    return final_pixel, (x,z)

def work(param_list):
    pixel_x, focus_x, focus_y, focus_z, image_array_attenuation, VOXEL_MM, final_pixel, image_array, receptor_plane, EMISSION_POINT = param_list
    list_pixels = []
    for pixel_y in range(40, 110): #range(start_y, end_y):
        for pixel_z in range(40, 110): #range(start_z, end_z):
            #receptor_z = receptor_plane_equation(receptor_x, receptor_y, a,b,c,d)

            #pixel_x, pixel_y, pixel_z = 45, 75, 75
            
            final_pixel, coords = ray(pixel_x, pixel_y, pixel_z, focus_x, focus_y, focus_z, image_array_attenuation, VOXEL_MM, final_pixel, image_array, EMISSION_POINT)
            
            # Calculate the intersection between the light beam and the projection plane
            # Parametric line equation

            #t =(125 - pixel_y)/(focus_y-pixel_y)

            #print(coords[0])
            #print(coords[1])
            #print("\n")

            #shared_data[int(coords[0]), int(coords[1])] = final_pixel    
            list_pixels.append([[int(coords[0]), int(coords[1])], final_pixel])
    return list_pixels

"""
def init_worker(receptor_plane_coords):
    # declare scope of a new global variable
    global shared_data
    # store argument in the global variable for this process
    
    shared_data = receptor_plane_coords    
"""

def project_blue_box(image_array, image_array_attenuation, configs, VOXEL_MM, W, H, D):

    # Create a array that will store the light intensity reached in each pixel of receptor plane
    receptor_plane = np.zeros((150, 150), dtype=np.float16)

    EMISSION_POINT = (149, 75, 75)

    POINT_FOCUS = [int(i) for i in configs['Blue_Box']['POINT_FOCUS'].split(",")]

    # Get the receptor plane parameters as a list containing [a, b, c, d], represeting parameters of a plane equation
    receptor_plane_coords = [int(i) for i in configs['Blue_Box']['RECEPTOR_PLANE'].split(",")]
    a = receptor_plane_coords[0]
    b = receptor_plane_coords[1]
    c = receptor_plane_coords[2]
    d = receptor_plane_coords[3]

    offset_x = round(W/2)
    offset_y = round(H/2)
    offset_z = round(D)

    start_z = (offset_z-70)
    end_z = (0+offset_z)
    start_x = (-15+offset_x)
    end_x = (15+offset_x)
    start_y = (-15+offset_y)
    end_y = (15+offset_y)

    focus_x = POINT_FOCUS[0] + offset_x
    focus_y = POINT_FOCUS[1] + offset_y
    focus_z = offset_z-POINT_FOCUS[2] 

    #plot3dModel(image_array[(offset_z-70):(0+offset_z), (-15+offset_x):(15+offset_x), (-15+offset_y):(15+offset_y)])
    #plot3dModel(image_array[start_z:end_z, start_x:end_x, start_y:end_y])
    #exit()

    #for receptor_x in np.linspace(0, 1):
    #    for receptor_y in np.linspace(-15, 15):
    final_pixel = 1

    start = time.time()
    param_list = []
    print("Construinfo a param list: ")
    for pixel_x in range(20, 150):#range(start_x, end_x):
        start = time.time()
        focus_x, focus_y, focus_z = 80, 155, 75
        param_list.append([pixel_x, focus_x, focus_y, focus_z, image_array_attenuation, VOXEL_MM, final_pixel, image_array, receptor_plane, EMISSION_POINT])
        #work(pixel_x, focus_x, focus_y, focus_z, image_array_attenuation, VOXEL_MM, final_pixel, image_array, receptor_plane)

    print("Executando o processo")
    with multiprocessing.Pool(24) as p:
        retorno = p.map(work, param_list)

    for process in retorno:
        for i in process:
            if i[0][0] >= 150 or i[0][1] >= 150:
                continue

            receptor_plane[i[0][0],i[0][1]] += 100-i[1]
    
    # Imagem resultante no plano de projeção é invertida. Vamos ajustar a sua orientação
    new = copy.deepcopy(receptor_plane)
    for i in range(receptor_plane.shape[0]):
        new[i, :] = receptor_plane[-i, :]
    receptor_plane = new

    end =time.time()
    print("Tempo decorrido para projetar uma linha do model: " + str(end-start))
    print(np.max(receptor_plane))
    print(np.min(receptor_plane))
    # Plot the 2D array as an image
    receptor_plane = ((receptor_plane - np.min(receptor_plane))/(np.max(receptor_plane)- np.min(receptor_plane))*255).astype(np.uint8)
    print(receptor_plane.shape)
    plt.imshow(receptor_plane, cmap='gray', vmin=0, vmax=255)  # You can choose a different colormap
    plt.colorbar()  # Add a colorbar for reference
    plt.show()        
    exit()


    end = time.time()
    print("3d model pixel: "+str(pixel_x)+ " " + str(pixel_y)+" " + str(pixel_z))
    print("Valor do pixel. Demorou:"+str(end-start))
    print(final_pixel)



    """
                            num_processes = multiprocessing.cpu_count()  # Use all available CPU cores
                        pool = multiprocessing.Pool(processes=num_processes)
                        results = pool.map(process_data, data_list)

                        
                        for t in np.linspace(0,30,1):
                            x0 = pixel_x
                            y0 = pixel_y
                            z0 = pixel_z

                            x = x0 + t*receptor_x
                            y = y0 + t*receptor_y
                            z = z0 + t*receptor_z

                            final_pixel -= final_pixel * image_array_attenuation[round(z/VOXEL_MM), round(x/VOXEL_MM), round(y/VOXEL_MM)]
    """




