import numpy as np
import matplotlib.pyplot as plt


def plot3dModel(model_3d):

    # Get the indices of non-zero values
    indices = np.where(model_3d == 255)
    #indices2 = np.where(model_3d == 254)

    # Create a figure and a 3D axis
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the 3D surface using the indices
    ax.scatter(indices[0], indices[1], indices[2], c='r', marker='o')
    #ax.scatter(indices2[0], indices2[1], indices2[2], c='b', marker='o')

    # Set labels for the axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()      