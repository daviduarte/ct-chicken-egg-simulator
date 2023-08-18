import numpy as np
import pydicom
from pydicom.dataset import FileDataset
from pydicom.uid import UID


# authors : Guillaume Lemaitre <g.lemaitre58@gmail.com>
# license : MIT

import datetime
import os
import tempfile

import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import UID


def create_dicom_dataset2(image_array, uid_prefix="1.2.826.0.1.3680043.9.7133.1.1."):

    # Create some temporary filenames
    suffix = '.dcm'
    filename_little_endian = "teste.dcm"#tempfile.NamedTemporaryFile(suffix=suffix).name
    filename_big_endian = tempfile.NamedTemporaryFile(suffix=suffix).name

    print("Setting file meta information...")
    # Populate required values for file meta information
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = UID('1.2.840.10008.5.1.4.1.1.2')
    file_meta.MediaStorageSOPInstanceUID = UID("1.2.3")
    file_meta.ImplementationClassUID = UID("1.2.3.4")

    print("Setting dataset values...")
    # Create the FileDataset instance (initially no data elements, but file_meta
    # supplied)
    ds = FileDataset(filename_little_endian, {},
                    file_meta=file_meta, preamble=b"\0" * 128)

    # Add the data elements -- not trying to set all required here. Check DICOM
    # standard
    ds.PatientName = "Simulated Data"
    ds.PatientID = "123456"

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

    print("Writing test file", filename_little_endian)
    ds.save_as(filename_little_endian)
    print("File saved.")

    # Write as a different transfer syntax XXX shouldn't need this but pydicom
    # 0.9.5 bug not recognizing transfer syntax
    ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRBigEndian
    ds.is_little_endian = False
    ds.is_implicit_VR = False

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

def create_dicom_dataset(image_array, uid_prefix="1.2.826.0.1.3680043.9.7133.1.1."):
    # Replace these values with appropriate DICOM metadata
    patient_name = "John Doe"
    study_date = "20230818"
    study_time = "120000"
    series_description = "CT Series"
    
    # Create a new DICOM dataset
    ds = FileDataset(None)  # Pass None to create an empty dataset
    ds.SOPClassUID = UID('1.2.840.10008.5.1.4.1.1.2')  # CT Image Storage SOP Class UID
    ds.SOPInstanceUID = pydicom.uid.generate_uid(uid_prefix)
    ds.PatientName = patient_name
    ds.StudyDate = study_date
    ds.StudyTime = study_time
    ds.Modality = "CT"
    ds.SeriesDescription = series_description
    
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
    
    return ds

# Replace this with your 3D NumPy array
#ct_array = np.random.choice([0, 255], size=(320, 320, 320), p=[0.95, 0.05]).astype(np.uint8)

# Create the DICOM dataset
#dicom_dataset = create_dicom_dataset(ct_array)

# Save the DICOM dataset to a file
#output_filename = "ct_series.dcm"
#dicom_dataset.save_as(output_filename)

#print(f"DICOM file saved as {output_filename}")