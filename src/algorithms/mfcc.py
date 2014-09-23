# -*- coding: utf-8 -*-

from scipy.fftpack import fft as FFT
import numpy as np

def mfcc(framewiseData, order = 60, samplerate = 48000, fftLen = None, low = 0, high = None):

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
  
  
  # Get the power spectrum
  powerSpectrum = spectrum(framewiseData, fftLen)
    
  # Get the filter banks    
  filters = filterBank(order, low, high, fftLen, samplerate)
  
  
  mfccs = np.log(np.dot(powerSpectrum, filters.T))
  mfccs = DCT(mfccs)
  
  
  
  return mfccs


def filterBank(order, low, high, fftLen, samplerate):
  centrePoints = fromMel(np.linspace(toMel(low), toMel(high), order + 2))
  centrePoints = np.round(fftLen*centrePoints/samplerate)
  
  bank = np.zeros((order, fftLen/2+1))
  for o in range(order):
    bank[o, centrePoints[o]:centrePoints[o+1]] = np.linspace(0, 1.0, centrePoints[o+1] - centrePoints[o] + 1)[1:]
    bank[o, centrePoints[o+1]:centrePoints[o+2]] = np.linspace(1.0, 0.0, centrePoints[o+2] - centrePoints[o+1] + 1)[:-1]
      
  return bank
  
def spectrum(data, fftLen = None):
  if fftLen is None:
    fftLen = data.shape[1]
  fftLen = int(fftLen)  
  return np.absolute(FFT(data),axis=1,n=fftLen)  
  
def DCT(data):
  N = data.shape[1]
  ret = np.zeros(data.shape)
  for k in range(N):
    ret(:,k) = np.sum(data*cos(np.pi*k/N*(np.arrange(1,N+1) - 0.5)))
  return np.sqrt(2.0/N)*ret  
  
def toMel(x):
  """ Converts x from Hz to mel-scale """  
  return 2595*np.log10(1+x/700)  

def fromMel(x):
  """ Converts x from mel-scale to Hz """  
  return 700*(10**(x/2595.0)-1)  
