""" Convenience functions to load example datasets """

import os
import scarplet as sl


EXAMPLE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'data/')


def load_carrizo():
    """
    Load sample dataset containing fault scarps along the San Andreas Fault
    from the Wallace Creek section on the Carrizo Plain, California, USA

    Data downloaded from OpenTopography and collected by the B4 Lidar Project:
    https://catalog.data.gov/dataset/b4-project-southern-san-andreas-and-san-jacinto-faults
    """

    path = os.path.join(EXAMPLE_DIRECTORY, 'carrizo.tif')
    data = sl.load(path)
    return data


def load_grandcanyon():
    """
    Load sample dataset containing part of channel network in the Grand Canyon
    Arizona, USA

    Data downloaded from the Terrain Tile dataset, part of Amazon Earth on AWS
    https://registry.opendata.aws/terrain-tiles/
    """

    path = os.path.join(EXAMPLE_DIRECTORY, 'grandcanyon.tif')
    data = sl.load(path)
    return data


def load_synthetic():
    """
    Load sample dataset of synthetic fault scarp of morphologic age 10 m2 
    """

    path = os.path.join(EXAMPLE_DIRECTORY, 'synthetic.tif')
    data = sl.load(path)
    return data
