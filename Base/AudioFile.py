# Contains file that can be heard, not parameters

import Numpy as np
import os
import warnings

class AudioFile:
  def self.__init__():
    self._name = ''
    self._fType = ''
    self._fRate = 0
    self._bitDepth = 0
    self._encoding = ''
    self._data = np.array()
    self._opened = False
    
  
    
  def self.Open(fileID, fType = 'raw', fRate = 48000, bitDepth=32, encoding='float', **kwargs):
    """ Generalised file opening """
    
    # function inputs
    defaults = {'fType':fType, 'fRate':fRate, 'fType':fType, 'encoding':'f', 'bitDepth':bitDepth}
    for key in kwargs:
      if key not in defaults.keys():
        raise ValueError('Unknown key in kwargs: ' + str(key))
    for key in defaults:
      if key not in kwargs.keys():
        kwargs[key] = defaults[key]
    fType = str(kwargs['fType'])
    fRate = float(kwargs['fRate'])
    bitDepth = int(kwargs['bitDepth'])
    encoding = str(kwargs['encoding'])
  
    try:
      fName = fileID.name
    except AttributeError:
      fName = str(fName)
      if not os.isfile(fName):
        raise IOError(fName + ' does not exist')
    self._name = fName
  
    # sort out the file type
    if fType = '':
      fType = os.path.splitext(fName)[1][1:]
    if fType[0] == '.': fType = fType[1:] 
    fType = fType.lower()
    validFileTypes = ['raw', 'ascii']
    if fType not in validFileTypes:
      warnings.warn('Unknown file type using raw')
      fType = 'raw'
      
    if fType == 'raw':
      self._openRaw(fileID, fRate, bitDepth, encoding)
    
    
    
  def self._openRaw(fileID, fRate, bitDepth, encoding):
    try:
      self._data = np.array()
      self._fType = 'raw'
      self._fRate = float(fRate)
      self._bitDepth = int(bitDepth) 
      self._encoding = str(encoding)
      self._opened = True
    except Exception as e:
      self._opened = False
      raise e
