# Contains speech features

import numpy as np
import os
import warnings
import AudioFile  

import algorithms 

class SpeechFeatures:
  """
  Speech features
  
  Features objects store the speech features extracted from an audio file and 
  provide the main interface for guiding the extraction.
  
  Methods
  -------
    clear:     Empties the data
    close:     Alias for clear
    setAudio:  Sets the input audio
    energy:    Returns framewise energy
    logEnergy: Returns framewise log energy
    mfcc:      Returns the framewise mfccs
    
  Attributes (should be treated as read only)
  ----------
    name:      The original file name
    mfccOrder: Order of the MFCCs if they have been calculated
    
    
  Private methods and attributes
  ------------------------------
    _audiofile:     AudioFile object
    _energy:        stored energy
    _logEnergy:     stored logEnergy 
    _mfcc:          stored coefficients   
  """
  
  def __init__(self, audiofile = None):
    self.clear()
    if audiofile:
      self.setAudio(audiofile)

  def clear(self):  
    self.name = None          # Source file name
    self.mfccOrder = None     # Order of the MFCCs
    
    self._audiofile = None    # Source file data
    self._energy    = None    # Stored version of the energy
    self._logEnergy = None    # Stored version of the log energy
    self._mfcc      = None    # MFCCs
    self._fftLen    = None    # FFT length defaults to whole frame
    
    
  def setAudio(self, audioFile):
    self.clear()  
    if isinstance(audioFile, AudioFile.AudioFile):  
      if audioFile.read:
        self._audiofile = audioFile
        self.name = self._audiofile.name
      else:
        raise IOError('In SpeechFeatures.setAudio input file is not read')  
    else:
      raise ValueError('SpeechFeatures.setAudio expects an AudioFile')  

  def energy(self):
    if (self._energy is None) or (self._logEnergy is None):
      self._energy, self._logEnergy = algorithms.energy(self._audiofile.window())
    return self._energy  

  def logEnergy(self):
    if (self._energy is None) or (self._logEnergy is None):
      self._energy, self._logEnergy = algorithms.energy(self._audiofile.window())
    return self._logEnergy   
    
  def mfcc(self, order = None, fftLen = None):
    
    if order is None: 
      if self.mfccOrder is None: 
        order = 60
      else:
        order = self.mfccOrder  
        
    if fftLen is None: 
      if self._fftLen is None: 
        fftLen = self._audiofile.window().shape[1]  
      else:
        fftLen = self._fftLen  

    if self._mfcc is None or (not self.mfccOrder == order) or (not fftLen == self._fftLen):
      self._audiofile.frame()
      emphasised = False
      if not self._audiofile.preemphasised:
        emphasised = True
        self._audiofile.preemphasise()

      self._mfcc = algorithms.mfcc(self._audiofile.window(), 
                                   order, 
                                   self._audiofile.rate,  
                                   fftLen,
                                   0, 
                                   self._audiofile.rate/2)
      if emphasised:
        self._audiofile.unemphasise() # if it was not preemphasised revert
      self.mfccOrder = self._mfcc.shape[1]
      self._fftLen = fftLen
    return self._mfcc 
    
  


if __name__ == '__main__':
  print "Testing Features module"
  
  af = AudioFile.AudioFile(os.path.join('..','demo','test.raw'))
  sf = SpeechFeatures()
  
  sf.setAudio(af)
  sf.energy()
  sf.logEnergy()
  sf.mfcc()
  
  
  import time
  
  print "Timing functions (seconds)"
  m = 10
  
  start = time.clock()
  for n in range(m):
    sf.setAudio(af)
    sf.energy()
  end = time.clock()
  print "Energy: {0}".format((end-start)/m)  
  
  start = time.clock()
  for n in range(m):
    af = AudioFile.AudioFile(os.path.join('..','demo','test.raw'))
    af.window('hanning')
    af.preemphasise()
    sf.setAudio(af)
    sf.mfcc()
  end = time.clock()
  print "MFCC:   {0}".format((end-start)/m)
       
  
  
  
  
  print "Done"
