


class Worker(object):

    def __init__(self):
        self.finished = False


class GridProcessor(Worker):

    def __init__(self):
        self.pid = os.getpid()
        self.age = None
        self.angle = None
        self.data_dir = None
        self.results_dir = None
    
    def set_data_dir(self, data_dir):
        self.data_dir = data_dir
    
    def set_results_dir(self, results_dir):
        self.results_dir = results_dir

    def match_template(self, age, angle):
        self.age = age
        self.angle = angle
        self.amp, self.snr = scarplet.match_template(self.data_dir, age, angle)

class Reducer(Worker):

    def __init__(self):
        self.best_fn = None
        self.results_fn = None

    def set_best_fn(self, best_fn):
        self.best_fn = best_fn
    
    def update_best_estimates(self, this_fn):
        best_params = np.load(self.best_fn)
        this_params = np.load(this_fn)

        mask = this_params[-1,:,:] > best_params[-1,:,:]
        best_params[:, mask] = this_params[:, mask]
        np.save(self.best_fn, best_params)
