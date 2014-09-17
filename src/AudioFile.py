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
    windowType: What type of window was used  
    windowNorm: What type of normalisation was used
    kaiserBeta: What was the value of the kaiser beta in the window
    
    
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
  _windowedData          The framed data that has been windowed
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
    self.windowType = None  # What type of window was used  
    self.windowNorm = None  # What type of normalisation was used
    self.kaiserBeta = None  # What was the value of the kaiser beta in the window
    
    # Private member functions
    self._frameshiftPT = None  # frame shift used for frame and window functions in data points
    self._framewidthPT = None  # frame length used for frame and window functions in data points
    self._framedData = None    # framed version of the data
    self._framedPadded = None  # Was the framed version padded
    self._framedCentred = None # Was the framed version centered if it was padded
    self._windowedData = None  # windowed version of the data 
    
    
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
      first sample is in the center of the first frame rather than the start (only relevant for padding), default true
      
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
          self._framedPadded = True
      else:
        self._framedPadded = not pad == False

      if centred is None:
        if self._framedCentred is None:
          self._framedCentred = True
      else:
        self._framedCentred = not centred == False    
    
      
      # convert to points from seconds
      self._frameshiftPT = int(self.frameshift * self.rate)
      if not (self.frameshift * self.rate).is_integer():
        warnings.warn('frame shift is not an integer frame shift in data points')
      
      self._framewidthPT = int(self.framewidth * self.rate)
      if not (self.framewidth * self.rate).is_integer():
        warnings.warn('frame width is not an integer frame shift in data points')
    

      
      if self._framedPadded:
        startInds = range(0, self.data.size, self._frameshiftPT)  
        self._framedData = np.zeros((len(startInds), self._framewidthPT))  
        
        if self._framedCentred:
          halfwidth = self._framewidthPT/2
          maxS = self.data.size - halfwidth; minS = halfwidth
          for i, s in enumerate(startInds):
            if s > minS and s < maxS:  
              self._framedData[i,:] = self.data[s-halfwidth:s+halfwidth,:].T
            else:
              if s < self._framewidthPT:  
                appendFrame = self.data[0:s+halfwidth,:].T 
                self._framedData[i, -appendFrame.size:] = appendFrame
              else:
                appendFrame = self.data[s-halfwidth:,:].T  
                self._framedData[i, :appendFrame.size] = appendFrame
        else:
          for i, s in enumerate(startInds):
            appendFrame = self.data[s:s+self._framewidthPT,:].T
            self._framedData[i, :appendFrame.size] = appendFrame  

      else:
        startInds = range(0,(self.data.size-self._framewidthPT), self._frameshiftPT)    
        self._framedData = np.zeros((len(startInds), self._framewidthPT))  
        for i, s in enumerate(startInds):
          self._framedData[i,:] = self.data[s:s+self._framewidthPT,:].T

          

      """      
      # This was used for finding the fastest method to do the framing
      # If you would like to try something else this is left for comparisons     

      import time    

      m = 10
      print 
      
      # pre-allocated numpy array 0.004 sec
      start = time.clock()
      for n in range(m):
          startInds = range(0,(self.data.size-self._framewidthPT), self._frameshiftPT)    
          self._framedData = np.zeros((len(startInds), self._framewidthPT))  
          for i, s in enumerate(startInds):
            self._framedData[i,:] = self.data[s:s+self._framewidthPT,:].T
      end = time.clock()
      print 'pre allocated numpy',
      print (end - start)/m
      
      # list comprehension 0.227 sec
      start = time.clock()
      for n in range(m):
          startInds = range(0,(self.data.size-self._framewidthPT), self._frameshiftPT)      
          self._framedData = [self.data[s:s+self._framewidthPT,:] for s in startInds]
          self._framedData = np.array(self._framedData).squeeze()
      end = time.clock()
      print 'list comprehension ',
      print (end - start)/m
      
      # numpy stacking  0.379 sec
      start = time.clock()
      for n in range(m):
          startInds = range(0,self.data.size-self._framewidthPT, self._frameshiftPT) 
          self._framedData = self.data[0:self._framewidthPT,:].T
          for s in startInds[1:]:
              self._framedData = np.vstack((self._framnumpy ndarrayedData, self.data[s:s+self._framewidthPT,:].T))

      end = time.clock()
      print 'numpy stacking     ',
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
      print 'list stacking      ',
      print (end - start)/m
      """
      
      return self._framedData
            
  def window(self, windowType = None, normalisation = None, kaiserBeta = None, **kwargs):
    """ Creates a windowed version of the framed data 
    
    This applies a windowing function to the framed data, if 
    the data was not framed it is done so. Several options 
    for window function and normalisation of the window function 
    are provided. The window function creates an array which 
    is then normalised if appropriate. This array is then elementwise
    multiplied into the framed data. If the data has already been
    windowed and no parameters are passed then it will reuse the existing
    windowed data parameters.
    
    Parameters
    ----------
    windowType {'blackman', 'bartlett', 'hamming', 'hanning', 'kaiser', 'rectangular', 'trapazoid'}, optional
      pick the window type. If kaiser is specified then the beta parameter must also be, 
      default is blackman
    normalisation {'none', 'sum', 'square sum'}, optional
      what form of normalisation to use on the window. If 'sum' then the array sums
      to one, if 'square sum', then the elementwise square sums to one, default is 'square sum'
    
    Keyword arguments
    -----------------
    frameshift: float, optional
      frame shift in seconds, default is to reuse from frame function
    framewidth: float, optional
      frame width in seconds
    pad: boolean, optional
      pad the framed data to the original length
    centred: boolean, optional
      centre the first frame     
    
    Returns
    -------
    numpy ndarray
      windowed version of the frames
      
    Raises
    ------
    ValueError if window type or normalisation type not recognised
    ValueError if kaiser is specified and no beta is provided
    """  
    
    defaults = {
      'windowType':windowType, 
      'normalisation':normalisation, 'normalization':normalisation,
      'kaiserBeta':kaiserBeta, 
      'frameshift':self.frameshift,
      'framewidth':self.framewidth,
      'pad':self._framedPadded,
      'centred':self._framedCentred,  'centered':self._framedCentred }
    for key in kwargs:
      if key not in defaults.keys():
        raise KeyError('Unknown key in AudioFile.window: ' + str(key))

    if 'centered' in kwargs.keys() and 'centred' in kwargs.keys():
      raise KeyError('"centered" and "centred" cannot both be defined')
    if 'normalization' in kwargs.keys() and 'normalisation' in kwargs.keys():
      raise KeyError('"normalisation" and "normalization" cannot both be defined')
    
    if 'centered' in kwargs.keys():
      kwargs['centred'] = kwargs['centered']
    if 'normalization' in kwargs.keys():
      kwargs['normalisation'] = kwargs['normalization']

    for key in defaults:
      if key not in kwargs.keys() + ['centered','normalization']:
        kwargs[key] = defaults[key]
    
    if kwargs['windowType'] is None:
      windowType = 'blackman'
    else:  
      windowType = kwargs['windowType'].lower()        
    if windowType not in ['blackman', 'bartlett', 'hamming', 'hanning', 'kaiser', 'rectangular', 'trapazoid']:
      raise ValueError('Unknown window function in AudioFile.window()') 
      
    if kwargs['normalisation'] is None:
      windowNorm = 'square sum'
    else:
      windowNorm = kwargs['normalisation'].lower()
    if windowNorm not in ['none', 'sum', 'square sum']:
      raise ValueError('Unknown normalisation in AudioFile.window()')   
    
    if windowType == 'kaiser':
      if kwargs['kaiserBeta'] is None:
        kwargs['kaiserBeta'] = self.kaiserBeta   
      try:
        self.kaiserBeta = float(kwargs['kaiserBeta'])
      except:
        raise ValueError('float beta value is needed for kaiser windowing')  

    # if nothing has changed then just return
    if windowType == self.windowType and windowNorm == self.windowNorm:
      if not self._windowFunction is None:
        if all([self._windowFunction.size == self._framewidthPT,
               kwargs['frameshift'] == self.frameshift, 
               kwargs['framewidth'] == self.framewidth,
               kwargs['pad'] == self._framedPadded, 
               kwargs['centred'] == self._framedCentred]):
          return self._windowedData
    
    # redo the framing       
    self.frame(kwargs['frameshift'], kwargs['framewidth'], kwargs['pad'], kwargs['centred'])
    
    windowSize = self._framewidthPT
    self.windowType = windowType
    self.windowNorm = windowNorm

    # get the window    
    if   self.windowType == 'blackman':    self._windowFunction = np.blackman(windowSize)    
    elif self.windowType == 'bartlett':    self._windowFunction = np.bartlett(windowSize)      
    elif self.windowType == 'hamming':     self._windowFunction = np.hamming(windowSize)      
    elif self.windowType == 'hanning':     self._windowFunction = np.hanning(windowSize)      
    elif self.windowType == 'kaiser':      self._windowFunction = np.kaiser(windowSize, kaiserBeta)      
    elif self.windowType == 'rectangular': self._windowFunction = np.ones((windowSize))      
    elif self.windowType == 'trapazoid':
      m1 = windowSize / 4   
      m2 = windowSize * 3 / 4;   
      slope = 4.0 / (windowSize - 1);   
      self._windowFunction = np.ones(windowSize)
      for k in range(m1):
        self._windowFunction[k] = k * slope  
      for i, k in enumerate(range(m2, windowSize)):
        self._windowFunction[k] = 4.0 - i * slope  
    
    self._windowFunction = np.array(self._windowFunction, ndmin = 2)    
    
    # normalise if needed
    if self.windowNorm == 'none': 
      pass
    elif self.windowNorm == 'sum':
      self._windowFunction = self._windowFunction / np.sum(self._windowFunction)  
    elif self.windowNorm == 'square sum':
      self._windowFunction = self._windowFunction / np.sum(np.square(self._windowFunction))

    # window the data
    self._windowedData = self._framedData * self._windowFunction
    
    return self._windowedData
    
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
    print ' done'
    
    print '   framing data ...',
    afRaw.frame(0.005,0.025,True,False)
    afRaw.frame(0.005,0.025,True,True)
    afRaw.frame(0.005,0.025,False,False)
    print ' done'
    
    print '   windowing data ...',
    afRaw.window('blackman', 'square sum')
    afRaw.window('bartlett', 'sum')
    afRaw.window('hamming', 'none')
    afRaw.window('hanning')
    afRaw.window('kaiser','square sum',0.5)
    afRaw.window('rectangular')
    afRaw.window('trapazoid')
    print ' done' 

    import time    
    afTest = AudioFile()
    testFile = os.path.join('..','demo','test.raw')
    
    start = time.clock()
    m = 100
    for n in range(m):
        afTest.clear()
        afTest.open(testFile)
        afTest.frame()
        afTest.window()
    end = time.clock()
    print "   average run time: {0}".format((end-start)/m)
    





