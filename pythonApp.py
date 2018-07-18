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

    INICIALIZATING_MSG = emoji.emojize(':eyes: Who is at front my door? System Started :thumbs_up: \n', use_aliases=True)
    DETECTED_MSG = emoji.emojize('Activity detected :exclamation: :exclamation: I am Looking for people.. :sleuth_or_spy:\n', use_aliases=True)
    FOUND_MSG = emoji.emojize('I Found something.. :scream:', use_aliases=True)
    NO_ONE_FOUND =  emoji.emojize('No one was found :man_shrugging:\n', use_aliases=True)
    MENU_OPTIONS = 'Available Commands: \n /rec - Send last recorded video \n /photos - Send last photos \n /help or /start - available commands'

    def handle(msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)

        if (content_type == 'text'):
            command = msg['text']
            print ('Got command: %s' % command)

        if  '/rec' in command:
            bot.sendMessage(chat_id, "Sending last REC...")
            path = './output.avi'
            if os.path.isfile(path):
                f = open(path, 'rb')
                bot.sendDocument(chat_id, f)
            else:
                bot.sendMessage(chat_id, "No REC found...")
        
        if  '/photos' in command:
            bot.sendMessage(chat_id, "Sending last photos...")
            notFound = 0
            for i in range(3):
                path = 'output_'+str(i)+'.jpg'
                if os.path.isfile(path):
                    f = open(path, 'rb')
                    bot.sendPhoto(CHAT_ID_API, f)
                else:
                    notFound += 1
            if notFound == 3:
                bot.sendMessage(chat_id, "No photos found...")
        
        if  '/help' in command:
            bot.sendMessage(chat_id, MENU_OPTIONS)

        if  '/start' in command:
            bot.sendMessage(chat_id, MENU_OPTIONS)

    arduino = serial.Serial("/dev/ttyUSB0", 9600, timeout=5)
    time.sleep(1)
    arduino.flush()

    # Cria um  bot com a API key disponibilizada pelo BotFather
    bot = telepot.Bot(TOKEN_API)
    
    # Adiciona a função hanldle para ser chamada sempre que uma nova mensagem for recebida do BOT
    MessageLoop(bot, handle).run_as_thread()
    bot.sendMessage(CHAT_ID_API, INICIALIZATING_MSG)
    bot.sendMessage(CHAT_ID_API, MENU_OPTIONS)
    print(INICIALIZATING_MSG)

    # adiciona classificador de reconhecimento de face
    face_cascade = cv2.CascadeClassifier('cascade_detections/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('cascade_detections/haarcascade_eye_tree_eyeglasses.xml')

    while True:
        arduino_data = arduino.readline()

        if (arduino_data):

            # Define o codec e o objeto que ira gerar o video, bem como a webCam utilizada e o nome do arquivo de saida
            cap = cv2.VideoCapture(0)

            start_time = time.time()
            time.clock() 

            print(DETECTED_MSG)

            bot.sendMessage(CHAT_ID_API, DETECTED_MSG)
            # fourcc = cv2.cv.CV_FOURCC(*'XVID') this line for openCv2 
            fourcc =  cv2.VideoWriter_fourcc(*'XVID') #this line for openCV3
            out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

            face_eyes_detect = 0

            while (arduino_data):
                #Captura frame-por-frame
                ret, frame = cap.read() 
                if ret==True:
                    frame = cv2.flip(frame,1)
                    frame_copy = frame.copy()

                    # # opcoes de cor do frame que ira incluir a camera
                    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    #escreve na saida cada frame flipado
                    
                    out.write(frame)

                    detect_face = face_cascade.detectMultiScale(frame)

                    for (x, y, w, h) in detect_face:
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
                        roi_frame = frame[y:y+h, x:x+w]
                        roi_color = frame[y:y+h, x:x+w]
                        eyes = eye_cascade.detectMultiScale(roi_frame)

                        out.write(frame)

                        if (len(eyes)):
                            for (ex,ey,ew,eh) in eyes:
                                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

                            out.write(frame)

                            if (face_eyes_detect < 3):

                                cv2.imwrite('orinal_'+str(face_eyes_detect)+'.jpg', frame_copy)
                                
                                print('-> unsharp image ' + str(face_eyes_detect))

                                gaussian = cv2.GaussianBlur(frame_copy, (9,9), 10.0)
                                unsharp_image = cv2.addWeighted(frame_copy, 1.5, gaussian, -0.5, 0, frame_copy)
                                
                                cv2.imwrite('unsharp_'+str(face_eyes_detect)+'.jpg', unsharp_image)

                                print('-> bluring image ROI  ' + str(face_eyes_detect))

                                blur = cv2.blur(unsharp_image,(5,5))
                                blur[y:y+h, x:x+w] = unsharp_image[y:y+h, x:x+w]
                                cv2.imwrite('output_'+str(face_eyes_detect)+'.jpg', blur)

                                face_eyes_detect += 1
                            else:
                                break

                    # Mostra a janela com a camera em escala de cinza
                    cv2.imshow('frame',frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'): # apertando 'q' no teclado a camera sera fechada
                        cap.release()
                        out.release()
                        cv2.destroyAllWindows()
                        break
                    if (time.time() - start_time) >= 10: #grava 15 segundos da tela para enviar ao BOT
                        cap.release()
                        out.release()
                        if face_eyes_detect == 0:
                            bot.sendMessage(CHAT_ID_API, NO_ONE_FOUND)

                        if (face_eyes_detect == 3):
                            bot.sendMessage(CHAT_ID_API, FOUND_MSG)
                        cv2.destroyAllWindows()
                        break
                else:
                    cap.release()
                    out.release()
                    cv2.destroyAllWindows()
                    break
        time.sleep(1)

    # Quando tudo estiver terminado fecha a camera
    cap.release()
    out.release()
    cv2.destroyAllWindows()
