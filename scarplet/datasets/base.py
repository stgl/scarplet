""" Convenience functions to load example datasets """

import os
import scarplet as sl


EXAMPLE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'data/')


def load_carrizo():
    path = os.path.join(EXAMPLE_DIRECTORY, 'carrizo.tif')
    data = sl.load(path)
    return data


def load_grandcanyon():
    path = os.path.join(EXAMPLE_DIRECTORY, 'grandcanyon.tif')
    data = sl.load(path)
    return data


def load_synthetic():
    path = os.path.join(EXAMPLE_DIRECTORY, 'synthetic.tif')
    data = sl.load(path)
    return data
