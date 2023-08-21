import numpy as np
import pydicom
from pydicom.dataset import FileDataset
from pydicom.uid import UID
import random
import string
import datetime
import os
import tempfile
import os
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import UID

#########
# GLOBALS
#########
W = 320  # 3D space width
H = 320  # 3D space height
D = 320   # 3D space depth

VOXEL_MM = 1

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


def save_slices(image_array, image_array_mask, configs, random_name, uid_prefix="1.2.826.0.1.3680043.9.7133.1.1."):

    slices, masks = extract_slices(image_array, image_array_mask, configs)


    # Create a folder in ./models
    # Check if the folder already exists
    if not os.path.exists(random_name):
        # Create the folder
        folder = os.path.join('models/slices', random_name)
        folder_mask = os.path.join('models/masks', random_name)
        os.makedirs(folder)
        os.makedirs(folder_mask)
    else:
        print(f"Folder '{folder}' already exists.")             
        raise NotImplemented


    cont = 0
    for i in range(len(slices)):

        #print("Setting file meta information...")
        # Populate required values for file meta information
        file_meta = FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = UID('1.2.840.10008.5.1.4.1.1.2')
        file_meta.MediaStorageSOPInstanceUID = UID("1.2.3")
        file_meta.ImplementationClassUID = UID("1.2.3.4")


        filename_little_endian = str(cont)+".dcm"        
        ds = FileDataset(filename_little_endian, {},
                        file_meta=file_meta, preamble=b"\0" * 128)

        # Add the data elements -- not trying to set all required here. Check DICOM
        # standard
        ds.PatientName = "Simulated Data"
        ds.PatientID = random_name

        # Set the transfer syntax
        ds.is_little_endian = True
        ds.is_implicit_VR = True

        # Set creation date/time
        dt = datetime.datetime.now()
        ds.ContentDate = dt.strftime('%Y%m%d')
        timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
        ds.ContentTime = timeStr

        # Convert the image array to a format suitable for DICOM (uint16)
        pixel_array = slices[i].astype(np.uint16)
        
        # Set the pixel data and related fields
        ds.PixelData = pixel_array.tobytes()
        ds.Rows, ds.Columns = slices[i].shape
        ds.BitsStored = 16
        ds.BitsAllocated = 16
        ds.HighBit = 15
        ds.RescaleIntercept = -1024  # Adjust as needed
        ds.RescaleSlope = 1    

        #print("Writing test file", filename_little_endian)
        ds.save_as(os.path.join(folder, filename_little_endian))
        #print("File saved.")

        # Write segmentation mask
        np.save(os.path.join(folder_mask, str(cont)+".npy"), masks[i])

        cont += 1
        #print("Writing test file as Big Endian Explicit VR", filename_big_endian)
        #ds.save_as(filename_big_endian)

        """
        # reopen the data just for checking
        for filename in (filename_little_endian, filename_big_endian):
            print('Load file {} ...'.format(filename))
            ds = pydicom.dcmread(filename)
            print(ds)

            # remove the created file
            print('Remove file {} ...'.format(filename))
            os.remove(filename)
        """

def save_3d_model(image_array, random_name):

    #print("Setting file meta information...")
    # Populate required values for file meta information
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = UID('1.2.840.10008.5.1.4.1.1.2')
    file_meta.MediaStorageSOPInstanceUID = UID("1.2.3")
    file_meta.ImplementationClassUID = UID("1.2.3.4")


    filename_little_endian = os.path.join("models/3d", random_name+".dcm")
    ds = FileDataset(filename_little_endian, {},
                    file_meta=file_meta, preamble=b"\0" * 128)

    # Add the data elements -- not trying to set all required here. Check DICOM
    # standard
    ds.PatientName = "Simulated Data"
    ds.PatientID = random_name

    # Set the transfer syntax
    ds.is_little_endian = True
    ds.is_implicit_VR = True

    # Set creation date/time
    dt = datetime.datetime.now()
    ds.ContentDate = dt.strftime('%Y%m%d')
    timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
    ds.ContentTime = timeStr

    # Convert the image array to a format suitable for DICOM (uint16)
    pixel_array = image_array.astype(np.uint16)
    
    # Set the pixel data and related fields
    ds.PixelData = pixel_array.tobytes()
    ds.Rows, ds.Columns, ds.NumberOfFrames = image_array.shape
    ds.BitsStored = 16
    ds.BitsAllocated = 16
    ds.HighBit = 15
    ds.RescaleIntercept = -1024  # Adjust as needed
    ds.RescaleSlope = 1    

    #print("Writing test file", filename_little_endian)
    ds.save_as(filename_little_endian)
    #print("File saved.")

    # Write as a different transfer syntax XXX shouldn't need this but pydicom
    # 0.9.5 bug not recognizing transfer syntax
    ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRBigEndian
    ds.is_little_endian = False
    ds.is_implicit_VR = False
 
def save_segmentation_mask(image_array_mask, random_name):
    path = os.path.join("models/masks", random_name+".npy")
    np.save(image_array_mask, path)

def create_dicom_dataset(image_array, model_3d_mask, configs, uid_prefix="1.2.826.0.1.3680043.9.7133.1.1."):

    name_lenght = 10
    characters = string.ascii_lowercase + string.digits
    random_name = ''.join(random.choice(characters) for _ in range(name_lenght))

    save_slices(image_array, model_3d_mask, configs, random_name, uid_prefix="1.2.826.0.1.3680043.9.7133.1.1.")
    save_3d_model(image_array, random_name)
