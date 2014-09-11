# Contains file that can be heard, not parameters

import Numpy as np
import os
import warnings

class AudioFile:
  def self.__init__():
    self._name = ''
    self._fType = ''
    self._fRate = 0
    self._fType = ''
    self._bitDepth = 0
    self._data = np.array()
    
  
    
  def self.Open(fileID, fType = '', fRate = 48000, fType = 'float', bitDepth=32, **kwargs):
    """ Generalised file opening """
    
    # function inputs
    defaults = {'fType':fType, 'fRate':fRate, 'fType':fType, 'bitDepth':bitDepth}
    for key in kwargs:
      if key not in defaults.keys():
        raise ValueError('Unknown key in kwargs: ' + str(key))
    for key in defaults:
      if key not in kwargs.keys():
        kwargs[key] = defaults[key]
    fType = kwargs['fType']
    fRate = kwargs['fRate']
    fType = kwargs['fType'] 
    bitDepth = kwargs['bitDepth']
  
    try:
      fName = fileID.name
    except AttributeError:
      fName = str(fName)
      if not os.isfile(fName):
        raise IOError(fName + ' does not exist')
  
    # sort out the file type
    if fType = '':
      fType = os.path.splitext(fName)[1][1:]
    if fType[0] == '.': fType = fType[1:] 
    fType = fType.lower()
    validFileTypes = ['raw', 'ascii']
    if fType not in validFileTypes:
      warnings.warn('Unknown file type using raw')
      
    if fType == 'raw':
      return _openRaw(fileID, fRate, fType, bitDepth)
    
    
    
  def self._openRaw(fileID, fRate, fType, bitDepth):
    pass
