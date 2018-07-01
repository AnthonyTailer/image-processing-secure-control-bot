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

while(1):
	arduino_data = arduino.readline()

	if (arduino_data):
		print(MY_MSG)
		bot.sendMessage(CHAT_ID_API, MY_MSG)
		# fourcc = cv2.cv.CV_FOURCC(*'XVID') this line for openCv2 
		fourcc =  cv2.VideoWriter_fourcc(*'XVID') #this line for openCV3
		out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
		i = 0
		while (arduino_data):
			#Captura frame-por-frame
			ret, frame = cap.read() 
			if ret==True:
				frame = cv2.flip(frame,1)
				
				#escreve na saida cada frame gravado
				out.write(frame)

				# opcoes de cor do frame que ira incluir a camera
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				
				# Mostra a janela com a camera em escala de cinza
				cv2.imshow('frame',gray)
			
				if cv2.waitKey(1) & 0xFF == ord('q'): # apertando 'q' no teclado a camera sera fechada
					break
				if i > 300: #grava cerca de 25 segundos da tela para enviar ao BOT
					break
			else:
				break
			i += 1
		f = open('output.avi', 'rb')
		bot.sendDocument(CHAT_ID_API, f)				
	time.sleep(1)

# Quando tudo estiver terminado fecha a camera
cap.release()
out.release()
cv2.destroyAllWindows()
