import pydicom
import numpy as np
import io

# ler ds
filename = "/home/denis/Documentos/egg-dataset/models/slices/1ywevurik7/150.dcm"
ds = pydicom.dcmread(filename)

buffer = io.BytesIO()
buffer.write(ds[0x7fe0, 0x0010].value)

oi = np.frombuffer(buffer.getvalue(), dtype=np.uint16).reshape(320,320)

print(oi.shape)