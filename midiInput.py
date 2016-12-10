import pygame
from pygame.mixer import music
import pygame.mixer
import midi as m
from mido import MidiFile, Message, MidiTrack, MetaMessage, bpm2tempo
import mido
import time


def checkForDevices():
	if midi.get_count() != 0:
		print "Found", midi.get_count(), "device(s)."

		for i in range(midi.get_count()):
			print midi.get_device_info(i)
		return True
	else:
		return False


def playMusic(music_file, num_repeats):
    """
    Note: music_file should be a .ogg
    stream music with mixer.music module in blocking manner
    this will stream the sound from disk while playing
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


def printMIDIMsg(msg):
	print msg

def constructMidiArray(num_voices, num_measures, beats_per_measure, ticks_per_beat):
	total_ticks = num_measures*beats_per_measure*ticks_per_beat
	midiArray = [[] for i in range(total_ticks)]
	print("Constructed midi array with", total_ticks, "ticks.")
	return midiArray

def buildMidiFileFromArray(midi_array,bpm=56,ticks_per_beat=6,sig_num=6, sig_den=8, tempo_factor=0.5):
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
				event.time = tick - last_active_tick
				last_active_tick = tick
				track.append(event)
	# save the file to memory: will overwrite!
	mid.save('new_song.mid')
	return mid


def main():
	organ_file = './Dataset/mids/final_proj_organ.mid'
	bass_file = './Dataset/mids/final_proj_bass.mid'
	music_file = 'happy_bflat_blues.ogg'
	bpm = 56 # quarters per minute
	tempo = bpm2tempo(bpm)
	print tempo

	# create a midi file to store the recording session to
	mid = MidiFile(type=0)
	mid.ticks_per_beat = 6
	track = MidiTrack()
	mid.tracks.append(track)
	micros_per_beat = bpm2tempo(bpm)
	tempo_msg = MetaMessage('set_tempo', tempo=bpm2tempo(bpm))
	time_sig_msg = MetaMessage('time_signature', numerator=6, denominator=8)
	track.append(tempo_msg)
	track.append(time_sig_msg)
	# track.append(Message('note_on', note=64, velocity=64, time=2))
	# track.append(Message('note_off', note=64, velocity=127, time=2))
	# right now just saving a couple notes as a test #


	# create an array to store all midi objects in
	midArr = constructMidiArray(6,8,3,6)

	# play the backing track
	playMusic(music_file, 0)

	# open a port to receive midi events
	port = mido.open_input()
	recordTime = 22 # sec
	startTime = time.time()

	#keep track of when last midi message happened
	prev_msg_stamp_millis = startTime

	currentTick = 0
	while(currentTick < 144):

		#look for available messages
		msg = port.receive()
		# msg_stamp_millis = time.time() # get current msg time
		# dt = msg_stamp - prev_msg_stamp # get the time elapsed since last message
		# prev_msg_stamp = msg_stamp

		#convert seconds to elapsed to ticks
		# ticks_since_last_msg = int(6 * float(dt*1e6) / (float(micros_per_beat) * 0.5))
		
		currentTick = int(6*float(time.time()-startTime)*1e6 / (micros_per_beat))

		midArr[currentTick].append(msg)s

	buildMidiFileFromArray(midArr)


# align recording with tempo
# play the backing midi track with software instruments
# extract relevant information from the midi backing track
# at each timestep, collect an input vector, and an output vector (the note that is heard)

if __name__ == '__main__':
	try:
		main()
	except(KeyboardInterrupt):
		port.close()
		pygame.quit()
		pygame.mixer.quit()





# midi.init()
	
	# if checkForDevices() == True:
	# 	guitar = midi.Input(0, 4)
	# else:
	# 	print "No MIDI output found. Make sure a virtual MIDI output exists."