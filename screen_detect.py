#!/usr/bin/env python
#
# Detect and display screen resolution in full screen mode
#

import os, pygame,math, time

def main():
	pygame.init()
	screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
	print screen.get_rect()
	time.sleep(5)

if __name__ == '__main__': main()    
