from Maix import GPIO
from fpioa_manager import fm
import sensor,lcd,time
import KPU as kpu
from machine import UART, PWM, Timer
import machine
import utime
import _thread
import ujson
import os

#Define uart pins and configurations
fm.register(24, fm.fpioa.UART1_RX, force=True)
fm.register(32, fm.fpioa.UART1_TX, force=True)
uart = UART(UART.UART1, 115200, read_buf_len=4096)
tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
S1 = PWM(tim, freq=50, duty=0, pin=14)

#object detection setup
classes = ['aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
task = kpu.load(0x500000)
anchor = (1.08, 1.19, 3.42, 4.41, 6.63, 11.38, 9.42, 5.11, 16.62, 10.52)
a = kpu.init_yolo2(task, 0.7, 0.3, 5, anchor)

#function to write an angle in the servo motor
def Servo(servo,angle):
    S1.duty((angle+90)/180*10+2.5)

#run the object recognition model
def object_recognition_task(target_object):

    lcd.init()
    #lcd.rotation(2)'
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    #sensor.set_vflip(1)
    sensor.run(1)
    clock = time.clock()

    #initialize the servo in position 0 degrees
    Servo(S1, 0)
    time.sleep(5)

    #create arrays of 80 positions
    rank_array = ([0 for x in range(80)])
    all_area   = ([0 for x in range(80)])
    location_x   = ([0 for x in range(80)])
    location_y   = ([0 for x in range(80)])


    while(True):
        #image capture
        clock.tick()
        img = sensor.snapshot()

        #object detection with yolo2
        objects = kpu.run_yolo2(task, img)

        # if objects are detected on camera by yolo:
        if objects:
            number_obj = 0
            count = 0
            id_area = 0

            for obj in objects:

                ##for each object detected the program will draw a rectangle around the object with his name and porcentage of confidence
                #img.draw_rectangle(obj.rect(),color=(0,255,0),thickness=3) #draw the rectangle
                #img.draw_string(obj.x(), obj.y(), classes[obj.classid()], color=(0,255,0),scale=2) #write the name of the object
                #img.draw_string(obj.x(), obj.y()+12, '%.3f'%obj.value(), color=(0,255,0),scale=2) #confidence value
                #name = classes[obj.classid()]  #get the name of the object

                if classes[obj.classid()] == target_object:

                    img.draw_rectangle(obj.rect(),color=(255,0,0),thickness=3)
                    img.draw_string(obj.x(), obj.y(), classes[obj.classid()], color=(255,0,0),scale=2)
                    img.draw_string(obj.x(), obj.y()+12, '%.3f'%obj.value(), color=(255,0,0),scale=2) #confidence value
                    #calculates the center cordinate of the object (centroid_x, centroid_y)
                    centroid_x = int(obj.w() / 2)
                    centroid_y = int(obj.h() / 2)

                    #save the centroid coordinate of each object in a array containing all objects centroid coordinates
                    location_x[number_obj] = obj.x() + centroid_x
                    location_y[number_obj] = obj.y() + centroid_y

                    #save the area of each object in a array containing all objects areas
                    all_area[number_obj] = obj.w() * obj.h()

                    #increase the index for the next object
                    number_obj +=1

                    #a = img.draw_circle(location_x[id_area], location_y[id_area], 3, color=(255, 0, 0), fill=True) #draw a circle on the center of the object with largest area
                    ##Calculates the percentage coordinates in relation to the image dimensions (320x240).
                    #percent_location_x = int(location_x[id_area] * 100 / 320) #x porcentage
                    #percent_location_y = int(location_y[id_area] * 100 / 240) #y porcentage

                    ##storages this relation in a json
                    #json_map = {}
                    #json_map["x"] = percent_location_x
                    #json_map["y"] = percent_location_y
                    #json_percent_location = ujson.dumps(json_map)
                    ##print(json_percent_location)

                    ##storages the x porcentage in a variable
                    #invert_px = percent_location_x
                    #print('proporcao:  ')
                    #print(invert_px)

                    ##set the limits of the porcentage value (0 - 100)
                    #in_min = 0
                    #in_max = 100
                    ##set the limits of the angle value (-90 - 90)
                    #out_min = -90
                    #out_max = 90

                    ##map function, or linear linearization of the inver_px value to the angle scale to get the angle of the servo:
                    #x = (invert_px - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
                    #print('angulo: ')
                    #print(x)

                    ##apply the x angle to the servo
                    #Servo(S1, int(x))

                    ##print(x)
                    #count += 1

                else:

                    #for each object detected the program will draw a rectangle around the object with his name and porcentage of confidence
                    img.draw_rectangle(obj.rect(),color=(0,255,0),thickness=3) #draw the rectangle
                    img.draw_string(obj.x(), obj.y(), classes[obj.classid()], color=(0,255,0),scale=2) #write the name of the object
                    img.draw_string(obj.x(), obj.y()+12, '%.3f'%obj.value(), color=(0,255,0),scale=2) #confidence value
                    name = classes[obj.classid()]  #get the name of the object



            #for j in range(number_obj):

                ##verify if the area of the object j has the bigger value on the rank_array to storage the largest area of all objects
                #if all_area[j] > rank_array[0]:
                    #rank_array[0]= all_area[j] #save the largest area on the rank_array[0]
                    #id_area = j    #save the id of the largest object

        #if rank_array[0] > 0 and obj:

                #a = img.draw_circle(location_x[id_area], location_y[id_area], 3, color=(255, 0, 0), fill=True) #draw a circle on the center of the object with largest area
                ##Calculates the percentage coordinates in relation to the image dimensions (320x240).
                #percent_location_x = int(location_x[id_area] * 100 / 320) #x porcentage
                #percent_location_y = int(location_y[id_area] * 100 / 240) #y porcentage

                ##storages this relation in a json
                #json_map = {}
                #json_map["x"] = percent_location_x
                #json_map["y"] = percent_location_y
                #json_percent_location = ujson.dumps(json_map)
                ##print(json_percent_location)

                ##storages the x porcentage in a variable
                #invert_px = percent_location_x
                #print('proporcao:  ')
                #print(invert_px)

                ##set the limits of the porcentage value (0 - 100)
                #in_min = 0
                #in_max = 100
                ##set the limits of the angle value (-90 - 90)
                #out_min = -90
                #out_max = 90

                ##map function, or linear linearization of the inver_px value to the angle scale to get the angle of the servo:
                #x = (invert_px - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
                #print('angulo: ')
                #print(x)

                ##apply the x angle to the servo
                #Servo(S1, int(x))

                ##print(x)
                #count += 1

        a = lcd.display(img) #refresh the display

        if uart.any():
            stop = uart.read()
            stop_decoded = stop.decode('utf-8')
            if stop_decoded == 'stop':
                kpu.deinit(task)
                lcd.clear()
                #uart.write(b'task-finish')
                #print('atividade finalizada')
                waiting_command()
        else:
            pass

#a = kpu.deinit(task) #close task

                #if var == 'cat':
                    #print('eh um gato')
        #img = img.resize(240,240)
        #lcd.display(img)
     #close task
    #kpu.deinit(task) #necessary?


#_thread.start_new_thread(serial_loop, ("1",))

def waiting_command():
    while True:
        if uart.any():
            command = uart.read()
            command_decoded = command.decode('utf-8')
            obj = command_decoded.split("-")
            print(obj[1])
            if obj[0] == 'bring':
                print('mensagem bring recebida!')
                object_recognition_task(obj[2])
            elif command_decoded == 'follow':
                print('mensagem follow')
                follow_task()

        #else:
            #print('sem mensagem')

#run the face recognition model
def follow_task():

    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)


    lcd.init()

    clock = time.clock()

    task = kpu.load("/sd/facedetect.kmodel")

    #face detection setup
    anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
    a = kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)

    while(True):
        clock.tick()
        img = sensor.snapshot()
        code = kpu.run_yolo2(task, img)

        if code:
            for i in code:
                print(i)
                b = img.draw_rectangle(i.rect())

        lcd.display(img)

        print(clock.fps())

        if uart.any():
            stop = uart.read()
            stop_decoded = stop.decode('utf-8')
            if stop_decoded == 'stop':
                kpu.deinit(task)
                lcd.clear()
                print('atividade finalizada')
                waiting_command()
        else:
            pass


while True:
    waiting_command()





