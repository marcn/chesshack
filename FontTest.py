#!/usr/bin/env python

import os, pygame, math, random, time, thread, sys, string
import numpy as np
from pygame.locals import *

screen = pygame.display.set_mode((800, 800))
screen.fill((16,16,16))
pygame.display.flip()
pygame.init()
y = 0
for font_name in pygame.font.get_fonts():
	print font_name
	try:
		#font = pygame.font.SysFont(font_name, 15)
		font = pygame.font.SysFont("Courier New", 30, bold=True)
		surface = font.render("Your Move", True, (0, 0, 255))
		screen.blit(surface, (100, y))
		y += surface.get_rect().h
	except Exception:
		pass

pygame.display.flip()
time.sleep(10)