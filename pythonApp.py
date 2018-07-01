#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial
import time
import numpy as np
import cv2
import telepot
from telepot.loop import MessageLoop

TOKEN_API = '603549957:AAGk9ghYJ_XFLg-BWLuz7k8lMIWzxfh8By8'
CHAT_ID_API = "617138851"
MY_MSG = "\nALERTA DE PERIGO!!! \n\n Sua residência pode estar sendo invadida! Presença Detectada\n\n"

def handle(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	print(content_type, chat_type, chat_id)

	if (content_type == 'text'):
		command = msg['text']
		print ('Got command: %s' % command)
 
	if  '/Ola' in command:
		bot.sendMessage(chat_id, "Ola, como voce esta?")
	if  '/start' in command:
		bot.sendMessage(chat_id, "Sistema de segurança inicializado!!..")

# Define o codec e o objeto que ira gerar o video, bem como a webCam utilizada e o nome do arquivo de saida
cap = cv2.VideoCapture(0)


arduino = serial.Serial("/dev/ttyUSB0", 9600, timeout=5)
time.sleep(1)
arduino.flush()

# Cria um  bot com a API key disponibilizada pelo BotFather
bot = telepot.Bot(TOKEN_API)
 
# Adiciona a função hanldle para ser chamada sempre que uma nova mensagem for recebida do BOT
MessageLoop(bot, handle).run_as_thread()
bot.sendMessage(CHAT_ID_API, "Sistema de segurança inicializado!!")
print("Sistema de segurança inicializado!!..")

# adiciona classificador de reconhecimento de face
face_cascade = cv2.CascadeClassifier('cascade_detections/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('cascade_detections/haarcascade_eye_tree_eyeglasses.xml')

while(1):
	arduino_data = arduino.readline()

	if (arduino_data):
		print(MY_MSG)
		bot.sendMessage(CHAT_ID_API, MY_MSG)
		# fourcc = cv2.cv.CV_FOURCC(*'XVID') this line for openCv2 
		fourcc =  cv2.VideoWriter_fourcc(*'XVID') #this line for openCV3
		out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
		i = 0
		face_eyes_detect = False
		while (arduino_data):
			#Captura frame-por-frame
			ret, frame = cap.read() 
			if ret==True:
				frame = cv2.flip(frame,1)
				
				#escreve na saida cada frame gravado
				out.write(frame)

				# opcoes de cor do frame que ira incluir a camera
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				
				equalize_gray_image = cv2.equalizeHist(gray)

				detect_face = face_cascade.detectMultiScale(equalize_gray_image)

				for (x, y, w, h) in detect_face:
					cv2.rectangle(equalize_gray_image,(x,y),(x+w,y+h),(255,0,0),2)
        			roi_gray = equalize_gray_image[y:y+h, x:x+w]
        			roi_color = frame[y:y+h, x:x+w]
					
					eyes = eye_cascade.detectMultiScale(roi_gray)
        			if (len(eyes)):
						for (ex,ey,ew,eh) in eyes:
            				cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
						if (face_eyes_detect == False):
							face_eyes_detect = True
							cv2.imwrite('output.jpg', equalize_gray_image)
				# Mostra a janela com a camera em escala de cinza
				cv2.imshow('frame',equalize_gray_image)


			
				# if cv2.waitKey(1) & 0xFF == ord('q'): # apertando 'q' no teclado a camera sera fechada
				# 	break
				if i > 300: #grava cerca de 25 segundos da tela para enviar ao BOT
					break
			else:
				break
			i += 1
		f = open('output.jpg', 'rb')
		bot.sendDocument(CHAT_ID_API, f)				
	time.sleep(1)

# Quando tudo estiver terminado fecha a camera
cap.release()
out.release()
cv2.destroyAllWindows()
