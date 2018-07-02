#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial
import time
import numpy as np
import cv2
import telepot
from telepot.loop import MessageLoop
import json
import emoji

import os, sys

if len(sys.argv) < 3:
    print("Specify a TOKEN as argv[1] and a CHAT_ID as argv[2]")
    sys.exit(0)
else:

	TOKEN_API = sys.argv[1]
	CHAT_ID_API = sys.argv[2]

	INICIALIZATING_MSG = emoji.emojize(':eyes: Who is at front my door? starting.. :thumbs_up: \n', use_aliases=True)
	DETECTED_MSG = emoji.emojize('Activity detected :exclamation: :exclamation: I am Looking for people.. :sleuth_or_spy:\n', use_aliases=True)
	FOUND_MSG = emoji.emojize('I Found something.. :scream:', use_aliases=True)
	NO_ONE_FOUND =  emoji.emojize('No one was found :man_shrugging:\n', use_aliases=True)

	def handle(msg):
		content_type, chat_type, chat_id = telepot.glance(msg)
		print(content_type, chat_type, chat_id)

		if (content_type == 'text'):
			command = msg['text']
			print ('Got command: %s' % command)

	# Define o codec e o objeto que ira gerar o video, bem como a webCam utilizada e o nome do arquivo de saida
	cap = cv2.VideoCapture(0)

	arduino = serial.Serial("/dev/ttyUSB0", 9600, timeout=5)
	time.sleep(1)
	arduino.flush()

	# Cria um  bot com a API key disponibilizada pelo BotFather
	bot = telepot.Bot(TOKEN_API)
	
	# Adiciona a função hanldle para ser chamada sempre que uma nova mensagem for recebida do BOT
	MessageLoop(bot, handle).run_as_thread()
	bot.sendMessage(CHAT_ID_API, INICIALIZATING_MSG)
	print(INICIALIZATING_MSG)

	# adiciona classificador de reconhecimento de face
	face_cascade = cv2.CascadeClassifier('cascade_detections/haarcascade_frontalface_default.xml')
	eye_cascade = cv2.CascadeClassifier('cascade_detections/haarcascade_eye_tree_eyeglasses.xml')

	while(1):
		arduino_data = arduino.readline()

		if (arduino_data):
			start_time = time.time()
			print(DETECTED_MSG)
			bot.sendMessage(CHAT_ID_API, DETECTED_MSG)
			# fourcc = cv2.cv.CV_FOURCC(*'XVID') this line for openCv2 
			fourcc =  cv2.VideoWriter_fourcc(*'XVID') #this line for openCV3
			out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
			i = 0
			face_eyes_detect = 0

			while (arduino_data):
				#Captura frame-por-frame
				ret, frame = cap.read() 
				if ret==True:
					frame = cv2.flip(frame,1)
					
					#escreve na saida cada frame gravado
					out.write(frame)

					# opcoes de cor do frame que ira incluir a camera
					gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

					detect_face = face_cascade.detectMultiScale(gray)

					for (x, y, w, h) in detect_face:
						cv2.rectangle(gray,(x,y),(x+w,y+h),(255,0,0),2)
						roi_gray = gray[y:y+h, x:x+w]
						roi_color = gray[y:y+h, x:x+w]
						eyes = eye_cascade.detectMultiScale(roi_gray)

						if (len(eyes)):
							for (ex,ey,ew,eh) in eyes:
								cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

							if (face_eyes_detect < 3):

								equalize_gray_image = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
								
								bot.sendMessage(CHAT_ID_API, FOUND_MSG)

								print('-> equalizing image ' + str(face_eyes_detect))

								cv2.imwrite('output_'+str(face_eyes_detect)+'.jpg', equalize_gray_image)

								f = open('output_'+str(face_eyes_detect)+'.jpg', 'rb')

								bot.sendPhoto(CHAT_ID_API, f)

								print('-> sending image ' + str(face_eyes_detect))

								face_eyes_detect += 1
							else: 
								break

					# Mostra a janela com a camera em escala de cinza
					cv2.imshow('frame',gray)

					if cv2.waitKey(1) & 0xFF == ord('q'): # apertando 'q' no teclado a camera sera fechada
						break
					if (time.time() - start_time) >= 25: #grava cerca de 25 segundos da tela para enviar ao BOT
						if face_eyes_detect == 0:
							bot.sendMessage(CHAT_ID_API, NO_ONE_FOUND)
						break
				else:
					break
				i += 1
			if (time.time() - start_time) >= 25:
				break
		time.sleep(1)

	# Quando tudo estiver terminado fecha a camera
	cap.release()
	out.release()
	cv2.destroyAllWindows()
