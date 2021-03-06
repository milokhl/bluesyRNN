#!/usr/bin/env 

# Helper functions for bluesyRNN
# By Milo Knowles, 2016

import pygame
from pygame.mixer import music
import pygame.mixer
import midi as m
from mido import MidiFile, Message, MidiTrack, MetaMessage, bpm2tempo
import mido
import time
import numpy as np


def checkForDevices():
	if midi.get_count() != 0:
		print "Found", midi.get_count(), "device(s)."

		for i in range(midi.get_count()):
			print midi.get_device_info(i)
		return True
	else:
		return False

def getBeatArray_6_8():
	size = (3,18)
	beatArr = np.zeros(size,dtype=np.int8)

	beatArr[0][0], beatArr[0][6], beatArr[0][12] = 1,1,1
	beatArr[1][3], beatArr[1][6], beatArr[1][15] = 1,1,1
	beatArr[2][9], beatArr[2][12], beatArr[2][15] = 1,1,1

	return beatArr

def playMusic(music_file, num_repeats):
    """
    Note: music_file should be a .ogg filetype
    """
    clock = pygame.time.Clock()
    pygame.mixer.init()
    try:
        music.load(music_file)
        print "Music file %s loaded!" % music_file
    except pygame.error:
        print "File %s not found! (%s)" % (music_file, pygame.get_error())
        return False

    music.play(loops=num_repeats)
    return True

def constructMidiArray(num_measures, beats_per_measure, ticks_per_beat):
	"""
	beats_per_measure: # quarter notes in a measure (for 6/8 time, there are 3 quarter notes)
	ticks_per_beat: # of ticks we want slots for at each beat (6 ticks/beat means 3 ticks for each eighth note)
	num_measures: total # of measures in the form (i.e 8 or 12)

	Builds an array with a slot for each tick in the form.
	At each tick, stores another array of MIDI events, to allow for multiple notes at a time.
	"""
	total_ticks = num_measures*beats_per_measure*ticks_per_beat
	midiArray = [[] for i in range(total_ticks)]
	print("Constructed midi array with", total_ticks, "ticks.")
	return midiArray

def convertMidiSoloToTrainingArray(midi_file, num_ticks=144, num_pitches=43):
	"""
	Takes in a MIDI File (eg. 'my_midi.mid') of a solo, and converts to a 2D matrix, which is used for training.
	-Each column in the matrix represents a tick (timestep)
	-Each row in the matrix represents whether a note is articulated, held, or off at a given timestep
	-Notevalues are in [40,82] (low E, to high Bflat on guitar)
	-86 total rows in matrix, indexed 0,1,2,...,85
	-Note that this function expects only Track 0 in the midifile
	i_on = 2(notevalue-40)
	i_held = 2(notevalue-40)+1
	"""
	# create the training data array
	size = (num_pitches*2,num_ticks)
	trainingArr = np.zeros(size, dtype=np.int8)

	mid = MidiFile(midi_file)

	for i, track in enumerate(mid.tracks):

	    currentTick = 0
	    for msg in track:
	    	if not isinstance(msg, MetaMessage): # we don't want to consider meta messages
	    		print msg
		    	currentTick += msg.time # we skip forward by however long it was until we hit this message

		    	if currentTick != 0: #we must look back by msg.time steps (ex. if msg skips ahead by 2, we need to look back 2 columns)
		    		for step in range(-msg.time+1,1): # Note: when step=0, we are just checking the tick before currentTick
		    			tk = currentTick + step

			    		# if a note was articulated at last time step, it should be held unless instructed otherwise
			    		for j in range(trainingArr.shape[0]): #for each row

			    			if (j % 2) == 0: #an ON/OFF row
			    				if trainingArr[j][tk-1] == 1: #if we articulated this note at the last tick
			    					# it should be held at this tick
			    					trainingArr[j+1][tk] = 1
			    			else: #this is held/not held row
			    				if trainingArr[j][tk-1] == 1: #continue to hold an note if it was already being held
			    					trainingArr[j][tk] = 1

	    		# now look at the current message and make necessary updates
	    		if msg.type=='note_on':
	    			trainingArr[2*(msg.note-40)][currentTick] = 1 #turn note ON at current tick
	    			trainingArr[2*(msg.note-40)+1][currentTick] = 0 #turn held OFF
	    		elif msg.type=='note_off':
	    			trainingArr[2*(msg.note-40)][currentTick] = 0 #turn note OFF at current tick
	    			trainingArr[2*(msg.note-40)+1][currentTick] = 0 #turn held OFF
	return trainingArr

def createBackingArray(chords_with_duration, num_measures=8, beats_per_measure=3, ticks_per_beat=6):
	"""
	chords_with_duration: a list of tuples (root, quality, # beats held)
	eg. [(10,min_7,1.5), (8,maj,1.5), (1,maj_7,3), (3,min_7,1.5), (8,dom_7,1.5), (1,maj_7,3), 
		(6,maj_7,1.5), (5,dom_7,1.5),(10,min_7,1.5), (8,dom_7,1.5), (3,min_7,1.5), (8,dom_7,1.5), (1,maj_7,3)]
	C =0
	C#=1
	D =2
	D#=3
	E =4
	F =5
	F#=6
	G =7
	G#=8
	A =9
	A#=10
	B=11

	Creates a matrix representation of the chord progression
	-the [12] rows represent chord tones
	-each column is a tick
	"""
	# define chords intervalic structures that are used in a dict
	chord_dict = {'min_7':[0,3,7,10], 'maj_7':[0,4,7,11], 'dom_7':[0,4,7,10], 'maj':[0,4,7]}

	num_ticks = num_measures * beats_per_measure * ticks_per_beat
	size = (12, num_ticks)
	backingArr = np.empty(size, dtype=np.int8)
	backingArr.fill(-1)

	currentTick = 0
	for root, quality, duration in chords_with_duration:
		if duration*ticks_per_beat != int(duration*ticks_per_beat):
			print "Duration is not allowed: does not represent an whole number of ticks after conversion."
			raise(TypeError)
		for t in range(int(duration*ticks_per_beat)): # number of ticks for this chord
			for interval in chord_dict[quality]: # fill in the current chord at the current tick
				backingArr[(root+interval)%12][currentTick] = 1
			currentTick+=1

	return backingArr


def buildMidiFileFromArray(midi_array, filename='new_song.mid', bpm=56,ticks_per_beat=6,sig_num=6, sig_den=8, tempo_factor=0.5, min_note=40, max_note=82):
	"""
	midi_array: an array of midi events, indexed by tick
	sig_num: the numerator of the time signature
	sig_den: the denominator of the time signature
	tempo_factor: used to scale the speed of the midifile (use 0.5 to account for 6/8 vs. 6/4 weirdness)
	min_note: the lowest note that will be allowed
	max_note: the highest note that will be allowed

	Builds the midi file, saves it to the current directory, and returns it.
	"""
	#set up the midifile
	mid = MidiFile(type=0)
	mid.ticks_per_beat = ticks_per_beat
	track = MidiTrack()
	mid.tracks.append(track)
	micros_per_beat = bpm2tempo(bpm)
	tempo_msg = MetaMessage('set_tempo', tempo=int(bpm2tempo(bpm)*tempo_factor))
	time_sig_msg = MetaMessage('time_signature', numerator=sig_num, denominator=sig_den)
	track.append(tempo_msg)
	track.append(time_sig_msg)

	last_active_tick = 0
	for tick in range(len(midi_array)): # for each discrete tick index
		# the first event in at the current tick should have some offset
		# all other notes at the current tick should occur at the same time as the first event,
		# so give them zero offset
		if len(midi_array[tick]) == 0: # nothing happened at this tick
			continue
		else:
			for event in midi_array[tick]:
				# check if notes are within guitar playable range; if not, ignore
				if event.note > min_note and event.note < max_note:
					event.time = tick - last_active_tick
					last_active_tick = tick
					track.append(event)

	# save the file to memory: will overwrite!
	mid.save(filename)
	return mid

def recordSoloOverForm():
	### DEFINE PARAMETERS ###
	bpm = 56 # quarters per minute
	quarters_per_measure = 3
	measures_in_form = 8
	tempo = bpm2tempo(bpm) #this is the number of microseconds in a beat
	micros_per_beat = bpm2tempo(bpm)
	ticks_per_beat = 6
	sig_num = 6
	sig_den = 8

	# get midi files from backing track
	organ_file = './Dataset/mids/final_proj_organ.mid'
	bass_file = './Dataset/mids/final_proj_bass.mid'
	music_file = 'happy_bflat_blues.ogg'

	### END DEFINES ###

	# create a midi file to store the recording session to
	mid = MidiFile(type=0) #type 0 is a single track
	mid.ticks_per_beat = ticks_per_beat
	track = MidiTrack()
	mid.tracks.append(track)
	tempo_msg = MetaMessage('set_tempo', tempo=bpm2tempo(bpm))
	time_sig_msg = MetaMessage('time_signature', numerator=sig_num, denominator=sig_den)
	track.append(tempo_msg)
	track.append(time_sig_msg)

	# create an array to store all midi objects in
	midArr = constructMidiArray(measures_in_form,quarters_per_measure,ticks_per_beat)

	# play the backing track
	playMusic(music_file, 0)

	# open a port to receive midi events
	port = mido.open_input()
	recordTime = float(micros_per_beat)/1e6 * quarters_per_measure * measures_in_form
	print("Will record input for:", recordTime)
	startTime = time.time()

	# while we still have recording time
	currentTick = 0
	while(time.time() - startTime < recordTime):
		#wait for available messages, add them to slot in array
		msg = port.poll()	
		
		if msg != None:
			currentTick = min(143, int(6*float(time.time()-startTime)*1e6 / (micros_per_beat))) # do not allow tick to exceed max
			print(currentTick, msg)
			midArr[currentTick].append(msg)
	new_mid = buildMidiFileFromArray(midArr)
	return new_mid



def main():
	#recordSoloOverForm()
	#trainingArr = convertMidiSoloToTrainingArray('new_song.mid')
	#for i in trainingArr:
		#print i[0:30]
	
	chord_prog = [(10,'min_7',1.5), (8,'maj',1.5), (1,'maj_7',3), (3,'min_7',1.5), \
				(8,'dom_7',1.5), (1,'maj_7',3), (6,'maj_7',1.5), (5,'dom_7',1.5), \
				(10,'min_7',1.5), (8,'dom_7',1.5), (3,'min_7',1.5), (8,'dom_7',1.5), (1,'maj_7',3)]

	backingArr = createBackingArray(chord_prog)
	print backingArr
	

if __name__ == '__main__':
	try:
		main()
	except(KeyboardInterrupt):
		port.close()
		pygame.quit()
		pygame.mixer.quit()
