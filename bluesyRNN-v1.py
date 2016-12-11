#!/usr/bin/env 

# first stab at Bluesy-RNN
# By Milo Knowles, 2016
import numpy as np
import theano
from theano import tensor as T
from neuralmodels.layers import *
from neuralmodels.models import *
from neuralmodels.updates import Adagrad
from neuralmodels.costs import softmax_loss
from neuralmodels import loadcheckpoint

# import the helper library
from midiInput import *

# GATHER THE TRAINING DATA #
chord_prog = [(10,'min_7',1.5), (8,'maj',1.5), (1,'maj_7',3), (3,'min_7',1.5), \
			  (8,'dom_7',1.5), (1,'maj_7',3), (6,'maj_7',1.5), (5,'dom_7',1.5), \
			  (10,'min_7',1.5), (8,'dom_7',1.5), (3,'min_7',1.5), (8,'dom_7',1.5), (1,'maj_7',3)]

print "Creating backing track inputs."
backingArr = createBackingArray(chord_prog)
print backingArr

print "Creating beat encoding inputs."
beatArr = getBeatArray_6_8()
print beatArr

# PARAMETERS #
outputDim = 86
numPitchClasses = 43 # 60 different pitches, from low E on guitar to highest Bflat
midiRange = range(40, 83) #43 notes we can choose from [40, 82]


# training input parameters
time_steps = 144
num_sequences = 3
feature_dim = 102
trX_shape = (time_steps, num_sequences, feature_dim)

# TODO
# midi_file_1 = None
# midi_file_2 = None
# midi_file_3 = None
# trainingSolo1=convertMidiSoloToTrainingArray(midi_file_1)
# trainingSolo2=convertMidiSoloToTrainingArray(midi_file_2)
# trainingSolo3=convertMidiSoloToTrainingArray(midi_file_3)
# FINISH GATHERING TRAINING DATA #

# Input vector encoding
# [3] encoding of current beat (in 6/8 time, there are 18 triplet notes to consider)
# [1] fraction of current location in form (ex. 2nd measure of 4)
# [12] chord tones being played (-1 if not, 1 if chord tone)
# [86] notes held or articulated previous timestep, E1-Bflat4  possibly values (43 notes across 4 octaves)
# Total: [102]

# OUTPUT #
# [86] notes held or articulated previous timestep, E1-Bflat4 possibly values (43 notes across 4 octaves)

def buildtrX(training_solos, backing_arr, beat_arr, trX_shape):
	"""
	training_solos: a list of 2D training solo matrices
	backing_arr: a (12 x num_ticks) matrix representing the backing track chord progression
	beat_arr: an array representing the encoding of the beat

	Produces the training input matrix:
	-shape: (Num_ticks x Num_examples (solos) x Feature_dim)
	"""
	trX = np.array(trX_shape)

	# at each time step, build feature vectors for each sequence
	for tick in range(trX_shape[0]):

		# beats should repeat at some mod point (18 in this case)
		# we need to get the current tick column from the beat array
		currentBeatCode = beat_arr[:,tick % len(beat_arr[0])]

		# iterate through all the training solos we have
		for solo_index in len(training_solos):

			#build a feature vector for this solo
			feature_vect = []

			#add the current beat encoding
			feature_vect.append(currentBeatCode)

			#add the percentage of the form completed: current_tick / total_ticks
			feature_vect.append(float(tick) / trX_shape[2])

			# get the column from the backign array corresponding to current tick
			current_backing_harmony = backing_arr[:,tick % len(backing_arr[0])]
			feature_vect.append(current_backing_harmony)

			# finally, add the solo state vector from the previous tick as input
			if tick > 0:
				prev_solo_state = training_solos[solo_index][:,tick]
				feature_vect.append(prev_solo_state)

			# now put this feature vector in the right place in the trX matrix
			trX[tick][solo_index] = feature_vect

	return trX






# create a list of layers ot pass into the model class
layers = [TemporalInputFeatures(inputDim),LSTM(size=512),LSTM(size=512),LSTM(size=512),softmax(outputDim)]
trY = T.lmatrix()
initial_step_size = 1e-3 # the initial learning rate
model = RNN(layers,softmax_loss,trY,initial_step_size,Adagrad())

# fit the model with given parameters
model.fitModel(trX,trY,snapshot_rate=1,path=None,epochs=30,batch_size=50,learning_rate_decay=0.97,decay_after=10)


def main():
	pass

if __name__ == '__main__':
	main()