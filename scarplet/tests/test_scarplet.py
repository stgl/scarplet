import unittest
import dem
import WindowedTemplate as wt
import filecmp

class TemplateMatchingTestCase(unittest.TestCase):
    
    
    def setUp(self):
        
        self.dem = dem.DEMGrid('tests/data/synthetic.tif')

    def test_match_template(self):
        
        test_amplitude = dem.BaseSpatialGrid('tests/results/synthetic_amplitude.tif')
        test_age = dem.BaseSpatialGrid('tests/results/synthetic_age.tif')
        test_alpha = dem.BaseSpatialGrid('tests/results/synthetic_alpha.tif')

        template_args = {'alpha' : 0,
                         'kt' : 1,
                         'd' : 100 
                        }

        alpha = template_args['alpha']
        curv = self.dem._calculate_directional_lacpalcian(alpha)

        amplitude, age, alpha, snr = scarplet.match_template(curv, wt.Scarp.template_function, **template_args)
        
        # TODO: refactor into separate tests?
        with self.subTest(param_grid=amplitude):
            self.assertTrue(np.allclose(param_grid, test_amplitude), "Best-fit amplitudes incorrect")
        with self.subTest(param_grid=age):
            self.assertTrue(np.allclose(param_grid, test_age), "Best-fit ages incorrect")
        with self.subTest(param_grid=alpha):
            self.assertTrue(np.allclose(param_grid, test_alpha), "Best-fit orientations incorrect")


def generate_synthetic_scarp(a, b, kt, x_max, y_max, de=1, sig2=0, theta=0):
    """ Generate DEM of synthetic scarp for testing """
    
    nx = 2*x_max/de
    ny = 2*y_max/de
    x = np.linspace(-x_max, x_max, num=nx)
    y = np.linspace(-y_max, y_max, num=ny)
    x, y = np.meshgrid(x, y)
    
    theta = np.pi/2 - theta
    xrot = x*np.cos(theta) + y*np.sin(theta)
    yrot = -x*np.sin(theta) + y*np.cos(theta)

    z = -erf(yrot/(2*np.sqrt(kt))) + b*yrot
    z = z + sig2*np.random.randn(ny, nx)

    return set_up_grid(z, nx, ny, de) 

def set_up_grid(data, nx, ny, de):

    synthetic = dem.DEMGrid()
    geo_transform = (0, de, 0, 0, 0, -de) 
    projection = osr.SpatialReference()
    projection.ImportFromEPSG(DEFAULT_EPSG)

    synthetic._griddata = data 
    synthetic._georef_info.geo_transform = geo_transform
    synthetic._georef_info.projection = projection
    synthetic._georef_info.dx = de 
    synthetic._georef_info.dy = de 
    synthetic._georef_info.nx = nx 
    synthetic._georef_info.ny = ny
    synthetic._georef_info.xllcenter = 0 
    synthetic._georef_info.yllcenter = 0 

    return synthetic
