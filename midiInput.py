import pygame
from pygame import midi


def checkForDevices():
	if midi.get_count() != 0:
		print "Found", midi.get_count(), "device(s)."

		for i in range(midi.get_count()):
			print midi.get_device_info(i)
		return True
	else:
		return False



def main():
	midi.init()
	
	if checkForDevices() == True:
		guitar = midi.Input(0)
	else:
		print "No MIDI output found. Make sure a virtual MIDI output exists."

	while(True):
		if guitar.poll():
			print "Found input from guitar."

	guitar.close()


if __name__ == '__main__':
	main()