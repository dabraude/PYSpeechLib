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
    fType:    Type of audio file (eg raw)
    rate:     The sampling rate of the original audio in Hz (eg 48000)
    encoding: What type of data was stored [float, double, integer, short, char, ascii]
    bitDepth: The size of each sample (eg 16)
    data:     The original audio data
    
  Private methods and attributes
  ------------------------------
  _setEncoding(encoding) Sets the encoding following all rules
  _openRaw(endian)       Reads a raw file
  _openAscii()           Reads an ASCII file
  """
  
  
  def __init__(self, fileID = None, fType = 'raw', rate = 48000, encoding='float', bitdepth=32, **kwargs):
    """ Constructor, can be used as interface to Open """
    self.EncodingSubstitutions = {'f':'float',
                         's':'short',
                         'd':'double',
                         'u':'unsigned',
                         'unsigned integer':'unsigned',
                         'uint':'unsigned',
                         'i':'integer',
                         'c':'char',
                         'a':'ascii'}
    self.validEncodings = self.EncodingSubstitutions.keys() +  self.EncodingSubstitutions.values()
    
    self.clear()
    if fileID is not None:
      self.Open(fileID, fType, rate, encoding, bitdepth, **kwargs)

  def clear(self):
    """ Empties all variables """
    self.name = ''           # name of the orginal audio file
    self.fType = ''          # type of audio file e.g. wav or raw
    self.rate = 0            # sampling frequency of the source file in Hz
    self.bitdepth = 0        # size of each same (ASCII will be returned as None)
    self.encoding = ''       # type of encoding e.g. float
    self.data = np.array()   # the actual audio data
    self.read = False        # keeps track of if the file was sucessfully opened and read
    
  def close(self):
    """ Alias for clear """
    self.clear()
    
  def Open(self, fileID, fType = 'raw', rate = 48000, encoding='float', bitdepth=32, **kwargs):
    """ Generalised file opening 
    
    This is the interface for opening any audio file. If not opening a raw or ascii file none
    of optional values need to be set. 
    
    Parameters
    ----------
    fileID : string or file object
      File name or object to be read
    fType  : {'raw', 'ascii'}, optional
      Type of file to be read, default infered from the file name
    fRate  : integer (Hz), optional
      Sampling speed of the audio file, default 48000 if raw, otherwise always read from file and ignored
    encoding : {'f','s','u','i','c','a','d', 'float', 'short', 'unsigned', 'integer', 'char', 'ascii', 'double'}, optional
      Input format for raw files.
        float (f) = any bit depth floating point number
        unsigned (u) = any bit depth unsigned integer
        integer (i) = any bit depth signed integer
        double (d) = 64 bit float
        short (s) = 16 bit unsigned integer
        char (c) = 8 bit unsigned integer
        ascii (a) = ascii values, whitespace seperated
      default is float for raw values, otherwise always read from file and option is ignored
    bitdepth : integer, optional
      Number of bits per sample, default 32 for raw files, None for ascii, otherwise always read from file and ignored
    
    keyword only arguments (all optional):
    ----------------------
      endian = {'=','>','<'}
        endianess in order: (machine, big, little), default is machine, only used for raw files
    
    Returns
    -------
    boolean
      Returns if the file was sucessfully opened and read

    Raises
    ------
    KeyError
      If unknown key in keyword arguments
    IOError
      If file can not be found
    ValueError
      If endian is not understood in raw files
    """
    
    # function inputs
    defaults = {'fType':fType, 'rate':rate, 'encoding':encoding, 'bitdepth':bitDepth, 'endian':'='}
    for key in kwargs:
      if key not in defaults.keys():
        raise KeyError('Unknown key in AudioFile.Open: ' + str(key))
    for key in defaults:
      if key not in kwargs.keys():
        kwargs[key] = defaults[key]
  
    self.fileID = fileID
    
    self.rate = float(kwargs['rate'])
  

  
    if kwargs['bitDepth'] is None:
      self.bitdepth = None # for ASCII
    else:
      self.bitdepth = int(kwargs['bitDepth'])
  

  
    # get the file name
    try:
      self.name = fileID.name
    except AttributeError:
      self.name = str(fileID)
      if not os.isfile(self.name):
        raise IOError(fName + ' does not exist')

    # sort out the file type
    self.fType = str(kwargs['self.fType'])
    if self.fType = '':
      self.fType = os.path.splitext(self.name)[1][1:]
    if self.fType[0] == '.': self.fType = fType[1:] 
    self.fType = self.fType.lower()
    if self.fType == 'txt': self.fType = 'ascii'
    if self.encoding == 'ascii': self.fType = 'ascii'
    validFileTypes = ['raw', 'ascii']
    if self.fType not in validFileTypes:
      warnings.warn('Unknown file type, using raw')
      self.fType = 'raw'
    
    if self.fType == 'raw':
       # will also sort out the bitdepth
      self._setEncoding(str(kwargs['encoding']))
      return self._openRaw(kwargs['endian'])
    elif self.fType == 'ascii':
      self.encoding = None
      return self._openAscii()
    
    
  ### PRIVATE METHODS ###
    
  def _setEncoding(self,encoding):
    """ Sets the encoding for the file """
    if encoding is None:
      self.encoding = None
    if encoding in self.EncodingSubstitutions.keys():
      encoding = validEncodings[encoding]
    
    if encoding == 'double':
      self.encoding = 'float'
      self.bitdepth = 64
    elif encoding == 'short':
      self.encoding = 'unsigned'
      self.bitdepth = 16
    elif encoding == 'char':
      self.encoding = 'unsigned'
      self.bitdepth = 8
    elif encoding == 'ascii':
      self.encoding = 'ascii'
      self.bitdepth = None
    elif encoding in self.validEncodings:
      self.encoding = encoding
    else:
      warnings.warn('Unknown encoding, using float')
      self.encoding = 'float'
      
  def _openRaw(self, endian):
    """ Opens raw files """  
    try:
      dtype = ''
      if not endian == '=':
        if endian in ['>','<']:
          dtypes += endian
        else:
          raise ValueError('Unknown endian type')
      if self.encoding == 'float':
        dtype += 'f'
      elif self.encoding == 'unsigned':
        dtype += 'u'
      elif self.encoding == 'integer':
        dtype += 'i'
      else:
        raise ValueError('Unknown encoding')
      dtypeStr += str(self.bitdepth/8)
          
      self.data = np.array(np.fromfile(self.fileID, dtype=np.dtype(dtypeStr), count=-1, sep=''), ndmin=2)
      self.read = True
      return True
    except Exception as e:
      self.read = False
      raise e

  def _openAscii(self):
    """ Opens ASCII files """  
    try:
      self.data = np.loadtxt(self.fileID, ndmin = 2)
      self.bitDepth = None
      self.read = True
      return True
    except Exception as e:
      self.read = False
      raise e
