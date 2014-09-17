#########################################
# Base module
#########################################

import os
from src import *
from src.AudioFile import AudioFile

af = AudioFile()
af.open(os.path.join('demo','test.raw'))
af.frame()
af.window()

print af.length
