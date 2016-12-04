# first stab at Bluesy-RNN
# By Milo Knowles


import theano
from theano import tensor as T
from neuralmodels.layers import *
from neuralmodels.models import *
from neuralmodels.updates import Adagrad
from neuralmodels.costs import softmax_loss


# Input vector encoding
# [4] encoding of current beat (4 bit binary to represent 16 possible beats from 4/4 time)
# [1] fraction of current location in form (ex. 2nd measure of 4)
# [1] number of measures in a phrase (to allow for trading 4s, 8s, etc)
# [12] chord tones (-1 if not, 1 if chord tone)
# [120] notes held or articulated previous timestep, C1-C6 possibly values (60 notes across 5 octaves)

# OUTPUT #
# [120] notes held or articulated previous timestep, C1-C6 possibly values (60 notes across 5 octaves)
# [1] a silent output that blocks all other notes


# PARAMETERS #
inputDim = 138
initial_step_size = 1e-3 # the initial learning rate
numPitchClasses = 43 # 60 different pitches, from low E on guitar to highest Bflat
midiRange = range(40, 83) #43 notes we can choose from [40, 82]


# wtf is this
trY = T.lmatrix()

# END PARAMETERS #



#create a list of layers ot pass into the model class
layers = [TemporalInputFeatures(inputDim),LSTM(size=512),LSTM(size=512),LSTM(size=512),softmax(size=numClasses)]


# params: (layers,cost,Y,learning_rate,update_type=RMSprop(),clipnorm=0.0)
model = RNN(layers,softmax_loss,trY,initial_step_size,Adagrad())
