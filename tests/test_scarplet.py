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

        curv = self.dem._calculate_directional_lacpalcian(alpha)

        amplitude, age, alpha, snr = scarplet.match_template(curv, wt.Scarp.template_function, template_args)
        
        # TODO: refactor into separate tests?
        with self.subTest(param_grid=amplitude):
            self.assertTrue(np.equal(param_grid, test_amplitude), "Best-fit amplitudes incorrect")
        with self.subTest(param_grid=age):
            self.assertTrue(np.equal(param_grid, test_age), "Best-fit ages incorrect")
        with self.subTest(param_grid=alpha):
            self.assertTrue(np.equal(param_grid, test_alpha), "Best-fit orientations incorrect")
