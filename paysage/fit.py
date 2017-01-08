import numpy, time
from . import backends as B
from numba import vectorize
    
# -----  CLASSES ----- #
    
class SequentialMC(object):
    """SequentialMC
       Simple class for a sequential Monte Carlo sampler. 
    
    """
    def __init__(self, amodel, adataframe, method='stochastic'):
        self.model = amodel
        self.method = method
        try:
            self.state = adataframe.as_matrix().astype(numpy.float32)
        except Exception:
            self.state = adataframe.astype(numpy.float32)
        
    @classmethod
    def from_batch(cls, amodel, abatch, method='stochastic'):
        tmp = cls(amodel, abatch.get('train'), method=method)
        abatch.reset_generator('all')
        return tmp
        
    def update_state(self, steps):
        if self.method == 'stochastic':
            self.state = self.model.markov_chain(self.state, steps)  
        elif self.method == 'mean_field':
            self.state = self.model.mean_field_iteration(self.state, steps)  
        elif self.method == 'deterministic':
            self.state = self.model.deterministic_iteration(self.state, steps)  
        else:
            raise ValueError("Unknown method {}".format(self.method))
            
    def get_state(self, amodel):
        return self.state
            
            
class SequentialSimulatedTemperingImportanceResampling(object):
    
    def __init__(self, amodel, adataframe, method='stochastic'):
        self.model = amodel
        self.method = method
        try:
            self.state = adataframe.as_matrix().astype(numpy.float32)
        except Exception:
            self.state = adataframe.astype(numpy.float32)
        self.beta = numpy.ones((len(self.state), 1), dtype=numpy.float32)
        self.beta_stepsize = 0.01
        
    @classmethod
    def from_batch(cls, amodel, abatch, method='stochastic'):
        tmp = cls(amodel, abatch.get('train'), method=method)
        abatch.reset_generator('all')
        return tmp
        
    def update_state(self, steps):
        self.beta += self.beta_stepsize
        self.beta += self.beta_stepsize * numpy.random.randn(len(self.beta),1)
        #self.beta = reflect(self.beta).clip(0,1)
        self.beta = self.beta.clip(0,1)
        if self.method == 'stochastic':
            self.state = self.model.markov_chain(self.state, steps, self.beta)  
        elif self.method == 'mean_field':
            self.state = self.model.mean_field_iteration(self.state, steps, self.beta)  
        elif self.method == 'deterministic':
            self.state = self.model.deterministic_iteration(self.state, steps, self.beta)  
        else:
            raise ValueError("Unknown method {}".format(self.method))
        
    def get_state(self, amodel):
        current_energy = amodel.marginal_free_energy(self.state, self.beta)
        target_energy = amodel.marginal_free_energy(self.state, None)
        delta = current_energy - target_energy
        delta -= numpy.max(delta)
        weights = B.exp(delta)           
        weights /= B.msum(weights)
        indices = numpy.random.choice(numpy.arange(len(weights)), size=len(weights), replace=True, p=weights)
        return self.state[list(indices)] 


class TrainingMethod(object):
    
    def __init__(self, model, abatch, optimizer, epochs, skip=100, 
                 update_method='stochastic', sampler='SequentialMC'):
        self.model = model
        self.batch = abatch
        self.epochs = epochs
        self.update_method = update_method
        #self.sampler = SequentialMC.from_batch(self.model, self.batch, method=self.update_method)
        self.sampler = SSTIR.from_batch(self.model, self.batch, method=self.update_method)
        self.optimizer = optimizer
        self.monitor = ProgressMonitor(skip, self.batch)


class ContrastiveDivergence(TrainingMethod):
    """ContrastiveDivergence
       CD-k algorithm for approximate maximum likelihood inference. 
    
       Hinton, Geoffrey E. "Training products of experts by minimizing contrastive divergence." Neural computation 14.8 (2002): 1771-1800.
       Carreira-Perpinan, Miguel A., and Geoffrey Hinton. "On Contrastive Divergence Learning." AISTATS. Vol. 10. 2005.
    
    """
    def __init__(self, model, abatch, optimizer, epochs, mcsteps, skip=100, update_method='stochastic'):
        super().__init__(model, abatch, optimizer, epochs, skip=skip, update_method=update_method)
        self.mcsteps = mcsteps
        
    def train(self):
        for epoch in range(self.epochs):          
            t = 0
            start_time = time.time()
            while True:
                try:
                    v_data = self.batch.get(mode='train')
                except StopIteration:
                    break
                            
                # CD resets the sampler from the visible data at each iteration
                self.sampler = SequentialMC(self.model, v_data, method=self.update_method) 
                self.sampler.update_state(self.mcsteps)    
                
                # compute the gradient and update the model parameters
                v_model = self.sampler.get_state(self.model)
                self.optimizer.update(self.model, v_data, v_model, epoch)
                t += 1
                
            # end of epoch processing            
            prog = self.monitor.check_progress(self.model, 0, store=True)
            print('End of epoch {}: '.format(epoch))
            print("-Reconstruction Error: {0:.6f}, Energy Distance: {1:.6f}".format(*prog))

            end_time = time.time()
            print('Epoch took {0:.2f} seconds'.format(end_time - start_time), end='\n\n')            
            
            # convergence check should be part of optimizer
            is_converged = self.optimizer.check_convergence()
            if is_converged:
                print('Convergence criterion reached')
                break
        
        return None
             

class PersistentContrastiveDivergence(TrainingMethod):
    """PersistentContrastiveDivergence
       PCD-k algorithm for approximate maximum likelihood inference. 
    
       Tieleman, Tijmen. "Training restricted Boltzmann machines using approximations to the likelihood gradient." Proceedings of the 25th international conference on Machine learning. ACM, 2008.
   
    """    
    def __init__(self, model, abatch, optimizer, epochs, mcsteps, skip=100, update_method='stochastic'):
       super().__init__(model, abatch, optimizer, epochs, skip=skip, update_method=update_method)
       self.mcsteps = mcsteps
    
    def train(self):
        for epoch in range(self.epochs):          
            t = 0
            start_time = time.time()
            while True:
                try:
                    v_data = self.batch.get(mode='train')
                except StopIteration:
                    break
                            
                # PCD keeps the sampler from the previous iteration
                self.sampler.update_state(self.mcsteps)    
    
                # compute the gradient and update the model parameters
                v_model = self.sampler.get_state(self.model)
                self.optimizer.update(self.model, v_data, v_model, epoch)
                t += 1
                
            # end of epoch processing            
            prog = self.monitor.check_progress(self.model, 0, store=True)
            print('End of epoch {}: '.format(epoch))
            print("-Reconstruction Error: {0:.6f}, Energy Distance: {1:.6f}".format(*prog))
            
            end_time = time.time()
            print('Epoch took {0:.2f} seconds'.format(end_time - start_time), end='\n\n')  
            
            # convergence check should be part of optimizer
            is_converged = self.optimizer.check_convergence()
            if is_converged:
                print('Convergence criterion reached')
                break
        
        return None
        
             
class ProgressMonitor(object):
    
    def __init__(self, skip, abatch, update_steps=10):
        self.skip = skip
        self.batch = abatch
        self.steps = update_steps
        self.num_validation_samples = self.batch.num_validation_samples()
        self.memory = []

    def reconstruction_error(self, model, v_data):
        sampler = SequentialMC(model, v_data) 
        sampler.update_state(1)   
        return numpy.sum((v_data - sampler.state)**2)
        
    def energy_distance(self, model, v_data):
        """energy_distance(model, v_data)
        
           Székely, Gábor J., and Maria L. Rizzo. "Energy statistics: A class of statistics based on distances." Journal of statistical planning and inference 143.8 (2013): 1249-1272.
        
        """
        v_model = model.random(v_data)
        sampler = SequentialMC(model, v_model) 
        sampler.update_state(self.steps)
        return len(v_model) * B.fast_energy_distance(v_data, sampler.state, downsample=100)
        
    def check_progress(self, model, t, store=False):
        if not (t % self.skip):
            recon = 0
            edist = 0
            while True:
                try:
                    v_data = self.batch.get(mode='validate')
                except StopIteration:
                    break
                recon += self.reconstruction_error(model, v_data)
                edist += self.energy_distance(model, v_data)
            recon = numpy.sqrt(recon / self.num_validation_samples)
            edist = edist / self.num_validation_samples
            if store:
                self.memory.append([recon, edist])
            return [recon, edist]
            
# ----- FUNCTIONS ----- #
    
@vectorize('float32(float32)', nopython=True)
def reflect(x):
    if 0 < x < 1:
        return x
    elif x <= 0:
        return -x
    else:
        return 2 - x
    

# ----- ALIASES ----- #
         
CD = ContrastiveDivergence
PCD = PersistentContrastiveDivergence
        
SSTIR = sstir = SequentialSimulatedTemperingImportanceResampling
