import RPi.GPIO as GPIO

Pin1 = 17
Pin2 = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(Pin1, GPIO.OUT)
GPIO.setup(Pin2, GPIO.OUT)
GPIO.output(Pin1, GPIO.LOW)
GPIO.output(Pin2, GPIO.LOW)





def set_switch(sw):
    
    match sw:
        case 1:
            GPIO.output(Pin1, GPIO.LOW)
            GPIO.output(Pin2, GPIO.LOW)
        
        case 0:
            GPIO.output(Pin1, GPIO.HIGH)
            GPIO.output(Pin2, GPIO.LOW)
        
        case 3:
            GPIO.output(Pin1, GPIO.LOW)
            GPIO.output(Pin2, GPIO.HIGH)
        

        case 2:
            GPIO.output(Pin1, GPIO.HIGH)
            GPIO.output(Pin2, GPIO.HIGH)



if __name__ == "__main__":
    set_switch(2) 
