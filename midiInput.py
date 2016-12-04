import pygame
from pygame import midi
from pygame.mixer import music
import pygame.mixer
import midi as m


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
        return

    music.play(loops=num_repeats)

    #while music.get_busy():
        # check if playback has finished
        #clock.tick(30)



# MIDI PACKET FORMAT #
# [[[status,data1,data2,data3],timestamp]
# ex. NOTE ON [[[144, note_value, velocity], time (millis)]]
# ex. NOTE OFF [[[128, note_value, velocity = 0], time (millis)]]


def main():
	#pygame.init()
	organ_file = './Dataset/mids/final_proj_organ.mid'
	bass_file = './Dataset/mids/final_proj_bass.mid'
	music_file = 'happy_bflat_blues.ogg'
	tempo = 56 # quarters per minute


	midi.init()
	
	if checkForDevices() == True:
		guitar = midi.Input(0, 4)
	else:
		print "No MIDI output found. Make sure a virtual MIDI output exists."

	# play the backing track
	playMusic(music_file, 4)

	try:
		while(True):
			if guitar.poll():
				#print "Found input from guitar."
				event = guitar.read(3)
				print event

	except(KeyboardInterrupt):
		guitar.close()
		midi.quit()
		pygame.quit()

# align recording with tempo
# play the backing midi track with software instruments
# extract relevant information from the midi backing track
# at each timestep, collect an input vector, and an output vector (the note that is heard)

if __name__ == '__main__':
	main()