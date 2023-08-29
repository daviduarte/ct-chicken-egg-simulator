import os
import numpy as np
import multiprocessing

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

def work(pixel_x, pixel_y, pixel_z, receptor_x, receptor_y, receptor_z, image_array_attenuation, VOXEL_MM):
    final_pixel = 100
    for t in np.linspace(0,30,1):
        x0 = pixel_x
        y0 = pixel_y
        z0 = pixel_z

        x = x0 + t*receptor_x
        y = y0 + t*receptor_y
        z = z0 + t*receptor_z

        final_pixel -= final_pixel * image_array_attenuation[round(z/VOXEL_MM), round(x/VOXEL_MM), round(y/VOXEL_MM)]    
        return final_pixel

def project_blue_box(image_array, image_array_attenuation, configs, VOXEL_MM):

    # Create a array that will store the light intensity reached in each pixel of receptor plane
    receptor_plane = np.zeros((320, 320), dtype=np.float16)

    # Get the receptor plane parameters as a list containing [a, b, c, d], represeting parameters of a plane equation
    receptor_plane_coords = [int(i) for i in configs['Blue_Box']['RECEPTOR_PLANE'].split(",")]
    a = receptor_plane_coords[0]
    b = receptor_plane_coords[1]
    c = receptor_plane_coords[2]
    d = receptor_plane_coords[3]

    print("Constrindo a bag list")

    arg_bag = []

    for receptor_x in np.linspace(0, 1):
        for receptor_y in np.linspace(-15, -15):
            final_pixel = 1
            for pixel_x in range(-15, 15):
                for pixel_y in range(-15, 15):
                    for pixel_z in range(-15, 15):
                        receptor_z = receptor_plane_equation(receptor_x, receptor_y, a,b,c,d)
                        arg_bag.append([pixel_x, pixel_y, pixel_z, receptor_x, receptor_y, receptor_z, image_array_attenuation, VOXEL_MM])

    print("Invocando os processos paralelos")
    num_processes = 8  # Use all available CPU cores
    pool = multiprocessing.Pool(processes=num_processes)    
    results = pool.map(work, arg_bag)



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


    print("porra")
    print(final_pixel)
    exit()

