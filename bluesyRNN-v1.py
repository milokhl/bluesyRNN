#!/usr/bin/env 

# first stab at Bluesy-RNN
# By Milo Knowles, 2016

import theano
from theano import tensor as T
from neuralmodels.layers import *
from neuralmodels.models import *
from neuralmodels.updates import Adagrad
from neuralmodels.costs import softmax_loss

from midiInput import *

# GATHER THE TRAINING DATA #
chord_prog = [(10,'min_7',1.5), (8,'maj',1.5), (1,'maj_7',3), (3,'min_7',1.5), \
			  (8,'dom_7',1.5), (1,'maj_7',3), (6,'maj_7',1.5), (5,'dom_7',1.5), \
			  (10,'min_7',1.5), (8,'dom_7',1.5), (3,'min_7',1.5), (8,'dom_7',1.5), (1,'maj_7',3)]

backingArr = createBackingArray(chord_prog)

beatArr = getBeatArray_6_8()
print beatArr

# TODO
# midi_file_1 = None
# midi_file_2 = None
# midi_file_3 = None
# trainingSolo1=convertMidiSoloToTrainingArray(midi_file_1)
# trainingSolo2=convertMidiSoloToTrainingArray(midi_file_2)
# trainingSolo3=convertMidiSoloToTrainingArray(midi_file_3)

# FINISH GATHERING TRAINING DATA #


# Input vector encoding
# [4] encoding of current beat (in 6/8 time, there are)
# [1] fraction of current location in form (ex. 2nd measure of 4)
# [1] number of measures in a phrase (to allow for trading 4s, 8s, etc)
# [12] chord tones being played (-1 if not, 1 if chord tone)
# [86] notes held or articulated previous timestep, E1-Bflat4  possibly values (43 notes across 4 octaves)

# OUTPUT #
# [86] notes held or articulated previous timestep, E1-Bflat4 possibly values (43 notes across 4 octaves)
# [1] a silent output that blocks all other notes


# PARAMETERS #
inputDim = 138
outputDim = 87
initial_step_size = 1e-3 # the initial learning rate
numPitchClasses = 43 # 60 different pitches, from low E on guitar to highest Bflat
midiRange = range(40, 83) #43 notes we can choose from [40, 82]


# # wtf is this
# trY = T.lmatrix()

# # END PARAMETERS #



# #create a list of layers ot pass into the model class
# layers = [TemporalInputFeatures(inputDim),LSTM(size=512),LSTM(size=512),LSTM(size=512),softmax(outputDim)]

# # params: (layers,cost,Y,learning_rate,update_type=RMSprop(),clipnorm=0.0)
# model = RNN(layers,softmax_loss,trY,initial_step_size,Adagrad())
def main():
	pass

if __name__ == '__main__':
	main()