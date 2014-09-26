# -*- coding: utf-8 -*-

from scipy.fftpack import fft as FFT
from scipy.fftpack import dct as DCT
import numpy as np

def mfcc(framewiseData, order = 60, samplerate = 48000, fftLen = None, low = 0, high = None): 
    """ Get the mel-frequency cepstral coefficients for the give data 
    
    Calculates the MFCCs of the data, it is assumed that the data is unbiased and pre-emphasised
  
    Parameters
    ----------
    framewiseData: numpy ndarray
        data to calculate mfccs for, each row is one frame
    order: int, optional 
        number of MFCCs to calculate, default 60
    samplerate: float, optional
        sample rate of the source audio in Hz, default 48000
    fftLen: int, optional
        length of fft used for calculations, default size of frame
    low: float, optional
        lowest frequency for fft bins in Hz, default 0
    high: float, optional
        highest frequency for fft bins in Hz, default samplerate / 2 
        
        
    Returns
    -------
    numpy ndarray
        mfccs, each row is one frame
    
    Raises
    ------
    ValueError    
    """  

    samplerate = float(samplerate)
    low = float(low)
    if high is None: 
        high = samplerate / 2 # niquest
    high = float(high)    
  
    if fftLen is None: 
        fftLen = framewiseData.shape[1]
    if float(fftLen).is_integer():     
        fftLen = int(fftLen)
    else:
        raise ValueError('FFT Length is not an integer')  

    spectrum = powerSpectrum(framewiseData, fftLen)
    filters = filterBank(order, low, high, fftLen, samplerate)
    # TODO: apply lifter
    mfccs = np.log(np.dot(spectrum, filters))
    mfccs = DCT(mfccs, type=2, norm='ortho')
    return mfccs

def filterBank(order, low, high, fftLen, samplerate):
    """ Create a triangular window filter bank """
    centrePoints = fromMel(np.linspace(toMel(low), toMel(high), order + 2))
    centrePoints = np.round(fftLen*centrePoints/samplerate)
  
    bank = np.zeros((order, fftLen/2))
    for o in range(order):
        bank[o, centrePoints[o]:centrePoints[o+1]] = np.linspace(0, 1.0, centrePoints[o+1] - centrePoints[o] + 1)[1:]
        bank[o, centrePoints[o+1]:centrePoints[o+2]] = np.linspace(1.0, 0.0, centrePoints[o+2] - centrePoints[o+1] + 1)[:-1]
      
    return bank.T
  
def powerSpectrum(data, fftLen):
    """ Calculate the framewise one tail power spectrum """
    fftLen = int(fftLen)  
    return np.absolute(FFT(data,axis=1,n=fftLen)[:,fftLen/2:])  
  
def toMel(x):
    """ Converts x from Hz to mel-scale """  
    return 2595*np.log10(1+x/700)  

def fromMel(x):
    """ Converts x from mel-scale to Hz """  
    return 700*(10**(x/2595.0)-1)  
