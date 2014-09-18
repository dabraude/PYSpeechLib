# Contains speech features

import numpy as np
import os
import warnings
import AudioFile
from algorithms import *

class SpeechFeatures:
  """
  Speech features
  
  Features objects store the speech features extracted from an audio file and 
  provide the main interface for guiding the extraction.
  
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
  def __init__(self):
    pass



if __name__ == '__main__':
  print "Testing Features module"