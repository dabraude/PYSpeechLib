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
        _fftLen:        FFT length for all analysis 
        _mfccLowBand:   Lowest band for the mel filters
        _mfccHighBand:  Highest band of the mel filters
    """

    def __init__(self, audiofile = None):
        """ Constructor 
        
        can function as an interface to setAudio
        
        Parameters
        ----------
        audioFile: {None, src.AudioFile.AudioFile}, optional 
            if an audio file is passed it will set the audio data
            to be the given object 
        """            
        self.clear()
        if audiofile:
            self.setAudio(audiofile)

    def clear(self):  
        """ Empties all variables """
        self.name          = None # Source file name
        self.mfccOrder     = None # Order of the MFCCs

        self._audiofile    = None # Source file data
        self._energy       = None # Stored version of the energy
        self._logEnergy    = None # Stored version of the log energy
        self._mfcc         = None # MFCCs
        self._fftLen       = None # FFT length defaults to whole frame
        self._mfccLowBand  = None # Lowest band for the mel filters
        self._mfccHighBand = None # Highest band of the mel filters
        
    def setAudio(self, audioFile):
        """ Sets the audio data for analysis
        
        The audio file must be open and read 
        
        Parameters
        ----------
        audioFile: src.AudioFile.AudioFile
            the source audio file
            
        Raises
        ------
        IOError: if the audio file has not been read
        ValueError: if the audiofile is not an src.AudioFile.AudioFile
        """
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
    
    def mfcc(self, order = None, fftLen = None, **kwargs):
        """ Calculate the MFCCs 
        
        Calculates the MFCCs as implemented in algorithms.mfcc 
        It only recalculates the MFCCs if any of the parameters
        have been changed
        
        Parameters
        ----------
        order: int, optional
            order of the MFCCs, default to previous value or 60 if none given before
        fftLen: int, optional
            window length for the FFT, defaults to whole frame
            
            
        Keyword arguments
        -----------------    
        lowBand: float, optional
            lowest band for the mel filters, default to previous or 0Hz
        highBand: float, optional
            highest band for the mel filters, default to previous or (sampling rate / 2)
            
        Returns
        -------
        Numpy ndarray
            MFCCs for each frame
        """
        defaults = {'order':order,'fftLen':fftLen,'lowBand':None, 'highBand':None}    
        for key in kwargs:
            if key not in defaults.keys():
                raise KeyError('Unknown key in SpeechFeatures.mfcc: {0}'.format(key))
        for key in defaults:
            if key not in kwargs.keys():
                kwargs[key] = defaults[key]
        
        if kwargs['order'] is None: 
            if self.mfccOrder is None: 
                order = 60
            else:
                order = self.mfccOrder            
        else:
            order = int(kwargs['order'])    
            
        if kwargs['fftLen'] is None: 
            fftLen = self._audiofile.window().shape[1]  
        else:
            fftLen = int(kwargs['fftLen']) 
        
        lowBand = kwargs['lowBand']
        if lowBand is None:
            if self._mfccLowBand is None:
                lowBand = 0
            else:
                lowBand = self._mfccLowBand
        else:
            lowBand = self._mfccLowBand
                
        highBand = kwargs['highBand']
        if highBand is None:
            if self._mfccHighBand is None:
                highBand = self._audiofile.rate/2
            else:
                highBand = self._mfccHighBand
        else:
            highBand = self._mfccHighBand
        
        
        if  self._mfcc is None \
            or (self.mfccOrder != order) \
            or (fftLen != self._fftLen) \
            or (lowBand != self._mfccLowBand) \
            or (highBand != self._mfccHighBand):
            
            self._audiofile.frame()
            emphasised = False
            if not self._audiofile.preemphasised:
                emphasised = True
                self._audiofile.preemphasise()
        
            self._mfcc = algorithms.mfcc(self._audiofile.window(), order, self._audiofile.rate, fftLen, lowBand, highBand)
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
    print "Energy: {0:.4f}".format((end-start)/m)  

    start = time.clock()
    for n in range(m):
        af = AudioFile.AudioFile(os.path.join('..','demo','test.raw'))
        af.window('hanning')
        af.preemphasise()
        sf.setAudio(af)
        sf.mfcc()
    end = time.clock()
    print "MFCC:   {0:.4f}".format((end-start)/m)
       




    print "Done"
