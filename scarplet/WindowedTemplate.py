# -*- coding: utf-8
""" Class for windowed template matching over a spatial grid """

import numexpr
import numpy as np

from scipy.special import erf, erfinv

np.seterr(divide='ignore', invalid='ignore')


class WindowedTemplate(object):
    """Base class for windowed template function

    Attributes
    ----------
    d : float
        Scale of windowed template function in data projection units
    alpha : float
        Orientation of windowed template function in radians
    c : float
        Curvature limit of template
    nx : int
        Number of columns in template array
    ny : int
        Number of rows in template array
    de : float
        Spacing of template grid cells in dat projection units

    Methods
    -------
    get_coordinates():
        Get arrays of coordinates for template grid points
    get_mask():
        Get mask array giving curvature extent of template window
    get_window_limits():
        Get mask array giving window extent
    """

    def __init__(self):

        self.d = None
        self.alpha = None
        self.nx = None
        self.ny = None
        self.c = self.nx / 2. 
        self.de = None

    def get_coordinates(self):
        x = self.de * np.linspace(1, self.nx, num=self.nx)
        y = self.de * np.linspace(1, self.ny, num=self.ny)
        x = x - np.mean(x)
        y = y - np.mean(y)

        x, y = np.meshgrid(x, y)
        xr = x * np.cos(self.alpha) + y * np.sin(self.alpha)
        yr = -x * np.sin(self.alpha) + y * np.cos(self.alpha)

        return xr, yr

    def get_mask(self):
        xr, yr = self.get_coordinates()
        mask = (abs(xr) < self.c) & (abs(yr) < self.d)
        return mask

    def get_window_limits(self):

        x4 = self.d*np.cos(self.alpha - np.pi/2)
        y4 = self.d*np.sin(self.alpha - np.pi/2)
        x1 = self.d*np.cos(self.alpha)
        y1 = self.d*np.sin(self.alpha)
        an_y = abs((x4 - x1) + 2 * self.c * np.cos(self.alpha - np.pi/2))
        an_x = abs((y1 - y4) + 2 * self.c * np.sin(self.alpha - np.pi/2))

        x = self.de*np.linspace(1, self.nx, num=self.nx)
        y = self.de*np.linspace(1, self.ny, num=self.ny)
        x = x - np.mean(x)
        y = y - np.mean(y)

        X, Y = np.meshgrid(x, y)
        mask = ((X < (min(x) + an_x)) | (X > (max(x) - an_x))
                | (Y < (min(y) + an_y)) | (Y > (max(y) - an_y)))

        return mask


class Scarp(WindowedTemplate):
    """Curvature template for vertical scarp

    Attributes
    ----------
    d : float
        Scale of windowed template function in data projection units
    alpha : float
        Orientation of windowed template function in radians
    kt : float
        Morphologic age of template in m2
    nx : int
        Number of columns in template array
    ny : int
        Number of rows in template array
    de : float
        Spacing of template grid cells in dat projection units

    Methods
    -------
    template():
        Returns array of windowed template function
    template_numexpr():
        Returns array of windowed template function optimized using numexpr

    References
    ----------
    Adapted from template derived in

    _[0] Hilley, G.E., DeLong, S., Prentice, C., Blisniuk, K. and Arrowsmith, 
         J.R., 2010. Morphologic dating of fault scarps using airborne 
         laser swath mapping (ALSM) data. Geophysical Research Letters, 37(4).
         https://dx.doi.org/10.1029/2009GL042044

    Based on solutions to the diffusion equation published in

    _[1] Hanks, T.C., 2000. The age of scarplike landforms from 
         diffusion‐equation analysis. Quaternary geochronology, 4, pp.313-338.

    and many references therein.
    """

    def __init__(self, d, kt, alpha, nx, ny, de):
        """Constructor method for scarp template

        Attributes
        ----------
        d : float
            Scale of windowed template function in data projection units
        kt : float
            Morphologic age of template in m2
        alpha : float
            Orientation of windowed template function in radians
        nx : int
            Number of columns in template array
        ny : int
            Number of rows in template array
        de : float
            Spacing of template grid cells in dat projection units
        """

        self.d = d
        self.kt = kt
        self.alpha = -alpha
        self.nx = nx
        self.ny = ny
        self.de = de

        frac = 0.9
        self.c = abs(2 * np.sqrt(self.kt) * erfinv(frac))

    def template(self):
        """Return template function

        Returns
        -------
        W : numpy array
            Windowed template function
        """

        x = self.de * np.linspace(1, self.nx, num=self.nx)
        y = self.de * np.linspace(1, self.ny, num=self.ny)
        x = x - np.mean(x)
        y = y - np.mean(y)

        x, y = np.meshgrid(x, y)
        xr = x * np.cos(self.alpha) + y * np.sin(self.alpha)
        yr = -x * np.sin(self.alpha) + y * np.cos(self.alpha)

        W = (-xr / (2. * self.kt ** (3 / 2.) * np.sqrt(np.pi))) \
            * np.exp(-xr ** 2. / (4. * self.kt))

        mask = self.get_mask()
        W = W * mask

        return W

    def template_numexpr(self):
        """Return template function (uses numexpr where possible)

        Returns
        -------
        W : numpy array
            Windowed template function
        """

        alpha = self.alpha
        kt = self.kt
        c = self.c
        d = self.d

        x = self.de * np.linspace(1, self.nx, num=self.nx)
        y = self.de * np.linspace(1, self.ny, num=self.ny)
        x = x - np.mean(x)
        y = y - np.mean(y)

        x, y = np.meshgrid(x, y)
        xr = numexpr.evaluate("x * cos(alpha) + y * sin(alpha)")
        yr = numexpr.evaluate("-x * sin(alpha) + y * cos(alpha)")

        pi = np.pi
        W = numexpr.evaluate("(-xr / (2 * kt ** (3/2) * sqrt(pi))) * \
                             exp(-xr ** 2 / (4 * kt))")

        mask = numexpr.evaluate("(abs(xr) < c) & (abs(yr) < d)")
        W = numexpr.evaluate("W * mask")

        return W


class RightFacingUpperBreakScarp(Scarp):
    """Template for upper slope break of vertical scarp (right-facting)

    Overrides template function to correct facign direction

    Attributes
    ----------
    d : float
        Scale of windowed template function in data projection units
    alpha : float
        Orientation of windowed template function in radians
    kt : float
        Morphologic age of template in m2
    nx : int
        Number of columns in template array
    ny : int
        Number of rows in template array
    de : float
        Spacing of template grid cells in dat projection units

    Methods
    -------
    get_error_mask():
        Return mask array that masks the lower slope break of scarp
    template():
        Returns array of windowed template function
    """

    def template(self):
        """Return template function (uses numexpr where possible)

        Returns
        -------
        W : numpy array
            Windowed template function
        """
        W = super().template_numexpr()
        return -W

    def get_err_mask(self):
        """Return mask array masking the lower half of scarp

        Returns
        -------
        mask : numpy array
            Mask array for lower half of scarp
        """
        xr, _ = self.get_coordinates()
        mask = xr <= 0
        return mask


class LeftFacingUpperBreakScarp(Scarp):
    """Template for upper slope break of vertical scarp (left-facting)

    Attributes
    ----------
    d : float
        Scale of windowed template function in data projection units
    alpha : float
        Orientation of windowed template function in radians
    kt : float
        Morphologic age of template in m2
    nx : int
        Number of columns in template array
    ny : int
        Number of rows in template array
    de : float
        Spacing of template grid cells in dat projection units

    Methods
    -------
    get_error_mask():
        Return mask array that masks the lower slope break of scarp
    """

    def get_err_mask(self):
        """Return mask array masking the lower half of scarp

        Returns
        -------
        mask : numpy array
            Mask array for lower hald of scarp
        """
        xr, _ = self.get_coordinates()
        mask = xr >= 0
        return mask


class ShiftedTemplateMixin(WindowedTemplate):
    """Mix-in for template that is offset from the window center

    Overrides template function to shift template

    Attributes
    ----------
    d : float
        Scale of windowed template function in data projection units
    alpha : float
        Orientation of windowed template function in radians
    kt : float
        Morphologic age of template in m2
    nx : int
        Number of columns in template array
    ny : int
        Number of rows in template array
    de : float
        Spacing of template grid cells in dat projection units
    dx : float
        X Offset of template center in data projection units
    dy : float
        Y Offset of template center data projection units

    Methods
    -------
    set_offset(dx, dy):
        Set offset attrivutes t odx and dy
    shift_template(W, dx, dy):
        Shift template array W by dx and dy
    template():
        Returns array of windowed template function
    """

    def __init__(self, *args, **kwargs):
        """Constructor for shifted template

        Parameters
        ----------
        dx : float
            X Offset of template center in data projection units
        dy : float
            Y Offset of template center data projection units
        """
        super().__init__(*args)
        self.set_offset(kwargs['dx'], kwargs['dy'])

    def set_offset(self, dx, dy):
        """Set offset values

        Parameters
        ----------
        dx : float
            X Offset of template center in data projection units
        dy : float
            Y Offset of template center data projection units
        """

        self.dx = dx
        self.dy = dy

    def shift_template(self, W, dx, dy):
        """Shift template

        Parameters
        ----------
        W : numpy array
            Windowed template function
        dx : float
            X Offset of template center in data projection units
        dy : float
            Y Offset of template center data projection units

        Returns
        -------
        W : numpy array
            Shifted windowed template function
        """

        ny, nx = W.shape

        if dx > 0:
            left = np.zeros((ny, dx))
            W = W[:, 0:-dx]
            W = np.hstack([left, W])
        else:
            dx = abs(dx)
            right = np.zeros((ny, dx))
            W = W[:, dx:]
            W = np.hstack([W, right])

        if dy > 0:
            bottom = np.zeros((dy, nx))
            W = W[0:-dy, :]
            W = np.vstack([W, bottom])
        else:
            dy = abs(dy)
            top = np.zeros((dy, nx))
            W = W[dy:, :]
            W = np.vstack([top, W])

        return W

    def template(self):
        """Template function for shifted template

        Returns
        -------
        W : numpy array
            Shifted windowed template function
        """

        W = super().template()
        W = self.shift_template(W, self.dx, self.dy)
        return W


class ShiftedLeftFacingUpperBreakScarp(ShiftedTemplateMixin,
                                       LeftFacingUpperBreakScarp):
    pass


class ShiftedRightFacingUpperBreakScarp(ShiftedTemplateMixin,
                                        RightFacingUpperBreakScarp):
    pass


class Ricker(WindowedTemplate):
    """Template using 2D Ricker wavelet

    Attributes
    ----------
    d : float
        Scale of windowed template function in data projection units
    alpha : float
        Orientation of windowed template function in radians
    kt : float
        Morphologic age of template in m2
    nx : int
        Number of columns in template array
    ny : int
        Number of rows in template array
    de : float
        Spacing of template grid cells in dat projection units

    Methods
    -------
    template():
        Returns array of windowed template function

    """

    def __init__(self, d, f, alpha, nx, ny, de):
        """Constructor method for Ricker template

        Paramters
        ---------
        d : float
            Scale of windowed template function in data projection units
        kt : float
            Morphologic age of template in m2
        alpha : float
            Orientation of windowed template function in radians
        nx : int
            Number of columns in template array
        ny : int
            Number of rows in template array
        de : float
            Spacing of template grid cells in dat projection units
        """

        self.d = d
        self.f = f
        self.alpha = -alpha
        self.nx = nx
        self.ny = ny
        self.c = nx
        self.de = de

    def get_window_limits(self):
        return np.zeros((self.ny, self.nx), dtype=bool)

    def template(self):
        """Template function for windowed Ricker wavelet 

        Returns
        -------
        W : numpy array
            Windowed template function
        """

        alpha = self.alpha
        d = self.d
        f = self.f

        xr, yr = self.get_coordinates() 

        pi = np.pi
        W = numexpr.evaluate("(1. - 2. * (pi * f * xr) ** 2.) * \
                             exp(-(pi * f * xr) ** 2.)")

        mask = self.get_mask()
        W = W * mask

        return W


class Channel(Ricker):
    """Duplicate class for Ricker wavelet used for fluvial channels"""
    pass


class Crater(WindowedTemplate):
    """Template for radially symmetric crater

    Attributes
    ----------
    r : float
        Radius of crater in pixels
    kt : float
        Morphologic age of template crater rim in m2
    nx : int
        Number of columns in template array
    ny : int
        Number of rows in template array
    de : float
        Spacing of template grid cells in dat projection units
    """

    def __init__(self, r, kt, nx, ny, de):
        """Constructor methodfor radially symmetric crater

        Parameters
        ----------
        r : float
            Radius of crater in pixels
        kt : float
            Morphologic age of template crater rim in m2
        nx : int
            Number of columns in template array
        ny : int
            Number of rows in template array
        de : float
            Spacing of template grid cells in dat projection units
        """

        self.r = r / de
        self.kt = kt
        self.nx = nx
        self.ny = ny
        self.de = de

    def template(self):
        """Template function for radially symmetric crater

        Returns
        -------
        W : numpy array
            Windowed template function
        """

        x = self.de * np.linspace(1, self.nx, num=self.nx)
        y = self.de * np.linspace(1, self.ny, num=self.ny)
        x = x - np.mean(x)
        y = y - np.mean(y)

        x, y = np.meshgrid(x, y)

        W = np.zeros_like(x)

        thetas = np.linspace(0, 2 * np.pi, num=359, endpoint=False)
        for theta in thetas:
            alpha = -theta
            dx = self.r * np.cos(theta)
            dy = self.r * np.sin(theta)
            xr = (x - dx) * np.cos(alpha) + (y + dy) * np.sin(alpha)
            yr = -(x - dx) * np.sin(alpha) + (y + dy) * np.cos(alpha)
            this_W = (-xr / (2. * self.kt ** (3 / 2.) * np.sqrt(np.pi))) \
                    * np.exp(-xr ** 2. / (4. * self.kt))

            mask = (abs(xr) < 1) & (abs(yr) < 5 / self.de)

            this_W *= mask

            if theta > np.pi / 2 and theta < 3 * np.pi / 2:
                this_W *= -1

            W += this_W

        return W
