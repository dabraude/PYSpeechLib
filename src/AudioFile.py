# Contains file that can be heard, not parameters

import numpy as np
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
    clear:  Empties the data
    close:  Alias for clear
    open:   Opens an audio file
    frame:  Returns a version of the file broken down into frames
    window: Returns a version of the file that has been broken down and had a windowing function applied
    
  Attributes (should be treated as read only)
  ----------
    read:       Returns if a file was opened and read
    name:       The original file name
    fType:      Type of audio file (eg raw)
    rate:       The sampling rate of the original audio in Hz (eg 48000)
    encoding:   What type of data was stored [float, double, integer, short, char, ascii]
    bitdepth:   The size of each sample (eg 16)
    data:       The original audio data
    length:     Length of the audio (sec)
    frameshift: Shift between frames in the current stored version
    framewidth: Length of the frames in the current stored version
    
    
  Private methods and attributes
  ------------------------------
  _setEncoding(encoding) Sets the encoding following all rules
  _openRaw(endian)       Reads a raw file
  _openAscii()           Reads an ASCII file
  _framedData            Framed version of the data
  _frameshiftPT          The frame shift in data points
  _framewidthPT          The frame length in data points
  _framedPadded          Was the frame padded
  _framedCentred         Was the frame centred
  """
  
  
  def __init__(self, fileID = None, fType = '', rate = 48000, encoding='float', bitdepth=32, **kwargs):
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
      self.open(fileID, fType, rate, encoding, bitdepth, **kwargs)

  def clear(self):
    """ Empties all variables """
    self.name = ''          # name of the orginal audio file
    self.fType = ''         # type of audio file e.g. wav or raw
    self.rate = 0           # sampling frequency of the source file in Hz
    self.bitdepth = 0       # size of each same (ASCII will be returned as None)
    self.encoding = ''      # type of encoding e.g. float
    self.data = None        # the actual audio data (numpy array)
    self.read = False       # keeps track of if the file was sucessfully opened and read
    self.length = 0.0       # length of the file in seconds
    self.frameshift = None  # frame shift used for frame and window functions in seconds
    self.framewidth = None  # frame length used for frame and window functions in seconds
    
    # Private member functions
    self._frameshiftPT = None  # frame shift used for frame and window functions in data points
    self._framewidthPT = None  # frame length used for frame and window functions in data points
    self._framedData = None    # framed version of the data
    self._framedPadded = None  # Was the framed version padded
    self._framedCentred = None # Was the framed version centered if it was padded
    
  def close(self):
    """ Alias for clear """
    self.clear()
    
  def open(self, fileID, fType = '', rate = 48000, encoding='float', bitdepth=32, **kwargs):
    """ Generalised file opening 
    
    This is the interface for opening any audio file. If not opening a raw or ascii file none
    of optional values need to be set. Does not preserve setting if reopening another file
    
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
    defaults = {'fType':fType, 'rate':rate, 'encoding':encoding, 'bitdepth':bitdepth, 'endian':'='}
    for key in kwargs:
      if key not in defaults.keys():
        raise KeyError('Unknown key in AudioFile.Open: ' + str(key))
    for key in defaults:
      if key not in kwargs.keys():
        kwargs[key] = defaults[key]
        
    self.clear()
  
    self.fileID = fileID
    
    self.rate = float(kwargs['rate'])
  
    if kwargs['bitdepth'] is None:
      self.bitdepth = None # for ASCII
    else:
      self.bitdepth = int(kwargs['bitdepth'])
  
    # get the file name
    try:
      self.name = fileID.name
    except AttributeError:
      self.name = str(fileID)
      if not os.path.isfile(self.name):
        raise IOError(self.name + ' does not exist')

    # sort out the file type
    self.fType = str(kwargs['fType'])
    if self.fType == '':
      self.fType = os.path.splitext(self.name)[1][1:]
    if self.fType[0] == '.': self.fType = fType[1:] 
    self.fType = self.fType.lower()
    if self.fType == 'txt' or self.encoding == 'ascii': 
        self.fType = 'ascii'
        kwargs['encoding'] = 'ascii'
    validFileTypes = ['raw', 'ascii']
    if self.fType not in validFileTypes:
      warnings.warn('Unknown file type, using raw')
      self.fType = 'raw'
    
    if self.fType == 'raw':
       # will also sort out the bitdepth
      self._setEncoding(str(kwargs['encoding']))
      self._openRaw(kwargs['endian'])
    elif self.fType == 'ascii':
      self.encoding = 'ascii'
      self._openAscii()
    
    
    if self.read:
      self.length = self.data.size / self.rate 
      return True
    else:
      return False        
    
    
    
  def frame(self, frameshift = None, framewidth = None, pad = None, centred = None,  **kwargs):
    """ Creates framed version of the file
    
    Creates a framed version of the data, or returns
    an existing framed version if no frame shift is specified
    and it was framed previously. Will also not recalculate
    if was already framed with the same frame shift and length.
    
    Parameters
    ----------
    frameshift: float (sec), optional
      Frame shift, if not specified will reuse the current value
      or default to 0.005 seconds
    framewidth: float (sec), optional
      Length of each frame, if not specified will reuse the current value
      or default to 0.020 seconds
    pad: boolean, optional
      zero pad the end (or start and end if centred) to bring to same length, default true 
    centered: boolean, optional
      frames are chosen from the centre rather than the start (only relevant for padding)
      
    Returns
    -------
    numpy ndarray
      framed version of the data
      
    Raises
    ------
    KeyError: unknown key in kwargs
    """  
        
    defaults = {'frameshift':frameshift, 'framewidth':framewidth, 'pad':pad, 'centred':centred, 'centered':centred}    
    for key in kwargs:
      if key not in defaults.keys():
        raise KeyError('Unknown key in AudioFile.frame: ' + str(key))
    for key in defaults:
      if key not in kwargs.keys():
        kwargs[key] = defaults[key]
    frameshift  = kwargs['frameshift']
    framelength = kwargs['framewidth'] 
    pad = kwargs['pad']
    centred = kwargs['centred'] or kwargs['centered']
    
    
    if (frameshift is None and framelength is None) and \
       not(self.frameshift is None and self.framewidth is None):
      # Existing version available and frameshift and framelength not specified  
      return self._framedData
    elif (frameshift == self.frameshift and framewidth == self.framewidth) and \
         (pad == self._framedPadded or pad is None) and \
         (not self._framedPadded  or (centred == self._framedCentred or centred is None)) and \
         not(self.frameshift is None and self.framewidth is None):
      # Existing version available and frameshift and framelength match that version
      print 'yes'
            
      return self._framedData  
    else:
      if frameshift is None:
        if self.frameshift is None:
          self.frameshift = 0.005
      else:
        self.frameshift = float(frameshift)
      
      if framewidth is None:
        if self.framewidth is None:
          self.framewidth = 0.025
      else:
        self.framewidth = float(framewidth)
    
      if pad is None:
        if self._framedPadded is None:
          self._framedPadded = False
      else:
        self._framedPadded = not pad == False

      if centred is None:
        if self._framedCentred is None:
          self._framedCentred = False
      else:
        self._framedCentred = not centred == False    
    
      
      # convert to points from seconds
      self._frameshiftPT = int(self.frameshift * self.rate)
      if not (self.frameshift * self.rate).is_integer():
        warnings.warn('frame shift is not an integer frame shift in data points')
      
      self._framewidthPT = int(self.framewidth * self.rate)
      if not (self.framewidth * self.rate).is_integer():
        warnings.warn('frame width is not an integer frame shift in data points')
    

    
      if not self._framedPadded:
        startInds = range(0,self.data.size-self._framewidthPT, self._frameshiftPT) 
        self._framedData = [self.data[0:self._framewidthPT,:].T]
        for s in startInds[1:]:
          self._framedData.append(self.data[s:s+self._framewidthPT,:].T)
        self._framedData = np.array(self._framedData).squeeze()   
      else:  
        if not self._framedCentred:
          startInds = range(0,self.data.size, self._frameshiftPT) 
          self._framedData = [self.data[0:self._framewidthPT,:].T]
          for s in startInds[1:]:
            appendFrame = self.data[s:s+self._framewidthPT,:].T
            appendFrame = np.hstack((appendFrame, np.zeros((1, self._framewidthPT - appendFrame.size))))
            self._framedData.append(appendFrame)
          self._framedData = np.array(self._framedData).squeeze() 
        else:
          startInds = range(self._frameshiftPT/2,self.data.size, self._frameshiftPT)   
          appendFrame = self.data[startInds[0]:startInds[0]+self._framewidthPT/2,:].T
          self._framedData = [np.hstack((np.zeros((1, self._framewidthPT - appendFrame.size)), appendFrame))]
          for s in startInds[1:]:
            if s > self._framewidthPT/2 and s < self.data.size - self._framewidthPT/2:
              appendFrame = self.data[s-self._framewidthPT/2:s+self._framewidthPT/2,:].T
            else:
              if s < self._framewidthPT:
                appendFrame = self.data[0:s+self._framewidthPT/2,:].T      
                appendFrame = np.hstack((np.zeros((1, self._framewidthPT - appendFrame.size)), appendFrame))
              else:
                appendFrame = self.data[s-self._framewidthPT/2:,:].T        
                appendFrame = np.hstack((appendFrame, np.zeros((1, self._framewidthPT - appendFrame.size))))
            self._framedData.append(appendFrame)
            
          self._framedData = np.array(self._framedData).squeeze() 
          


      """      
      # This was used for finding the fastest method to do the framing
      # If you would like to try something else this is left for comparisons     
      
      import time    

      m = 100

      # list comprehension 0.227 sec
      start = time.clock()
      for n in range(m):
          startInds = range(0,(self.data.size-self._framewidthPT), self._frameshiftPT)      
          self._framedData = [self.data[s:s+self._framewidthPT,:] for s in startInds]
          self._framedData = np.array(self._framedData).squeeze()
      end = time.clock()
      print 'list comprehension',
      print (end - start)/m
      
           
      
      # numpy stacking  0.379 sec
      start = time.clock()
      for n in range(m):
          startInds = range(0,self.data.size-self._framewidthPT, self._frameshiftPT) 
          self._framedData = self.data[0:self._framewidthPT,:].T
          for s in startInds[1:]:
              self._framedData = np.vstack((self._framedData, self.data[s:s+self._framewidthPT,:].T))

      end = time.clock()
      print 'numpy stacking    ',
      print (end - start)/m
      
      
      # list stacking  0.065 sec    
      start = time.clock()
      for n in range(m):
          startInds = range(0,self.data.size-self._framewidthPT, self._frameshiftPT) 
          self._framedData = [self.data[0:self._framewidthPT,:].T]
          for s in startInds[1:]:
              self._framedData.append(self.data[s:s+self._framewidthPT,:].T)
          self._framedData = np.array(self._framedData).squeeze()   
      end = time.clock()
      print 'list stacking     ',
      print (end - start)/m
      """
      
      
      
      
      
      return self._framedData
      
      

     
        
        
    
    
    
    
    
    
    
    
  ############### PRIVATE METHODS ###############
    
  def _setEncoding(self,encoding):
    """ Sets the encoding for the file """
    if encoding is None:
      self.encoding = None
    if encoding in self.EncodingSubstitutions.keys():
      encoding = self.EncodingSubstitutions[encoding]
    
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
      dtypeStr = ''
      if not endian == '=':
        if endian in ['>','<']:
          dtypeStr += endian
        else:
          raise ValueError('Unknown endian type')
      if self.encoding == 'float':
        dtypeStr += 'f'
      elif self.encoding == 'unsigned':
        dtypeStr += 'u'
      elif self.encoding == 'integer':
        dtypeStr += 'i'
      else:
        raise ValueError('Unknown encoding')
      dtypeStr += str(self.bitdepth/8)
          
      self.data = np.array(np.fromfile(self.fileID, dtype=np.dtype(dtypeStr), count=-1, sep=''), ndmin=2).T
      self.length = float(self.data.size) / self.rate
      self.read = True
      return True
    except Exception as e:
      self.read = False
      raise e

  def _openAscii(self):
    """ Opens ASCII files """  
    try:
      self.data = np.loadtxt(self.fileID, ndmin = 2)
      if self.data.shape[0] == 1: 
          self.data = self.data.T
      self.bitDepth = None
      self.read = True
      return True
    except Exception as e:
      self.read = False
      raise e
      
    except Exception as e:
        self.read = False
        raise e


if __name__ == '__main__':
    print 'Testing AudioFile module'
    
    print '   loading files ...',
    afOpen = AudioFile() # Create unopened object
    afOpen.open(os.path.join('..','demo','test.raw'), 'raw', 48000, 'float', 32) # Use open function
    afRaw = AudioFile(os.path.join('..','demo','test.raw')) # by filename
    afRaw = AudioFile(open(os.path.join('..','demo','test.raw'),'rb'),'raw') # with object
    afTxt = AudioFile(os.path.join('..','demo','test.txt'),'txt') # by filename
    afTxt = AudioFile(open(os.path.join('..','demo','test.txt'),'r'),'txt') # with object
    assert(afRaw.length == afTxt.length)
    assert(afRaw.length == afOpen.length)
    print ' done'
    
    print '   framing data ...',
    afRaw.frame(0.005,0.025,True,False)
    afRaw.frame(0.005,0.025,True,True)
    afRaw.frame(0.005,0.025,False,False)
    
    print ' done'
    
    

    
    
    





