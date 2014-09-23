import numpy as np

def energy(framedData):
   eng = np.sum(np.square(framedData), axis = 1) 
   logEng = np.log(eng)
   return (eng, logEng)