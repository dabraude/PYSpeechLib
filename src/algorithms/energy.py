import numpy as np

def energy(framedData):
    """ Calculate energy and log energy 

    Parameters
    ----------
        framedData: numpy ndarray
            data to calculate mfccs for, each row is one frame
            
    Returns
    -------
        (ndarray, ndarray)
            energy and log energy 
    """
    eng = np.sum(np.square(framedData), axis = 1) 
    logEng = np.log(eng)
    return (eng, logEng)