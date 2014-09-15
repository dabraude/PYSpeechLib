# Contains file that can be heard, not parameters

import Numpy as np
import os
import warnings

class AudioFile:
  """
  Audio file data
  
  Audio file objects store the raw data associated with a file and provide functionality
  for creating framed and windowed versions of the file for processing. Currently only supports
  mono file
  
  Methods
  -------
    Open:   Opens an audio file
    clear:  Empties the data
    close:  Alias for clear
    frame:  Returns a version of the file broken down into frames
    window: Returns a version of the file that has been broken down and had a windowing function applied
    
  Attributes (should be treated as read only)
  ----------
    read:     Returns if a file was opened and read
    name:     The original file name
    fType:    Type of audio file [raw]
    rate:     The sampling rate of the original audio in Hz (eg 48000)
    encoding: What type of data was stored [float, double, integer, short, char]
    bitDepth: The size of each sample (eg 16)
    data:     The original audio data
    
  
  """
  
  
  def __init__(self, fileID = None, fType = 'raw', fRate = 48000, encoding='float', bitDepth=None, **kwargs):
    """ Constructor, can be used as interface to open """
    if fileID is not None:
      self.Open(fileID, fType, fRate, encoding, **kwargs)
    else:
      self.clear()
    
  def clear(self):
    """ Empties all variables """
    self.name = ''           # name of the orginal audio file
    self.fType = ''          # type of audio file eg wav or raw
    self.rate = 0            # sampling frequency of the source file in Hz
    self.bitDepth = None     # size of each same (ASCII will be returned as None)
    self.encoding = ''       # type of encoding e.g. float
    self.data = np.array()   # the actual audio data
    self.read = False        # keeps track of if the file was sucessfully opened
    
  def close(self):
    """ Alias for clear """
    self.clear()
    
  def Open(self, fileID, fType = 'raw', fRate = 48000, encoding='float', bitDepth=None, **kwargs):
    """ Generalised file opening """
    
    # function inputs
    defaults = {'fType':fType, 'fRate':fRate, 'fType':fType, 'encoding':encoding, 'bitDepth':bitDepth}
    for key in kwargs:
      if key not in defaults.keys():
        raise ValueError('Unknown key in kwargs: ' + str(key))
    for key in defaults:
      if key not in kwargs.keys():
        kwargs[key] = defaults[key]
    fType = str(kwargs['fType'])
    fRate = float(kwargs['fRate'])
  
  
    encoding = str(kwargs['encoding'])
    validEncodings = {'f':'float',
                      's':'short',
                      'd':'double',
                      'i':'integer',
                      'c':'char',
                      'a':'ascii'}
    if encoding not in validEncodings.keys():
      encoding = validEncodings[encoding]
    elif encoding in validEncodings.values():
      encoding = encoding
    else:
      warnings.warn('Unknown encoding, using float')
      encoding = 'float'
  
  
    if not kwargs['bitDepth'] is None:
      bitDepth = int(kwargs['bitDepth'])
  
    try:
      fName = fileID.name
    except AttributeError:
      fName = str(fName)
      if not os.isfile(fName):
        raise IOError(fName + ' does not exist')
    self.name = fName
  
    # sort out the file type
    if fType = '':
      fType = os.path.splitext(fName)[1][1:]
    if fType[0] == '.': fType = fType[1:] 
    fType = fType.lower()
    validFileTypes = ['raw', 'ascii']
    if fType not in validFileTypes:
      warnings.warn('Unknown file type, using raw')
      fType = 'raw'
      
    if fType == 'raw':
      self._openRaw(fileID, fRate, encoding, bitDepth)
    
    
    
  def _openRaw(self, fileID, fRate, encoding, bitDepth = None):
    """ Opens raw files """  
    try:
      self.data = np.array()
      self.fType = 'raw'
      self.rate = float(fRate)
      self.encoding = str(encoding)
      self.bitDepth = int(bitDepth) 
      self.read = True
    except Exception as e:
      self.read = False
      raise e
