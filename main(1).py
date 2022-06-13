from myui import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore, QtGui
import threading
import os
import time 
import pigpio
import sys
import threading
import RPi.GPIO as GPIO
import pyqtgraph as pg
from pyqtgraph import plot

#import motor_control

class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle("Thrust bench GUI")
        self.display_lcd()
        self.label_16.setText("")
        self.label_11.setText("OFF")
        self.widget_2.setBackground('w')
        self.verticalSlider.setTickPosition(QtWidgets.QSlider.TicksLeft)
        self.verticalSlider.setTickInterval(5)
        self.pushButton.clicked.connect(lambda: self.onStartButton_click())
        self.pushButton_3.clicked.connect(lambda: self.calibrate_motor())
        self.t=threading.Thread(target=self.print_thrust)
        self.x=[]
        self.y=[]
    
    def print_thrust(self):
        EMULATE_HX711=False

        referenceUnit = 233016.888888889
        if not EMULATE_HX711:
            import RPi.GPIO as GPIO
            from hx711 import HX711
        else:
            from emulated_hx711 import HX711

        def cleanAndExit():
            print("Cleaning...")

            if not EMULATE_HX711:
                GPIO.cleanup()
        
            print("Bye!")
            sys.exit()

        hx = HX711(5, 6)
        hx.set_reading_format("MSB", "MSB")
        hx.set_reference_unit(referenceUnit)

        hx.reset()

        hx.tare()
        print("Tare done! Add weight now...")
        self.label_16.setText('Tare done')
        
        while True:
            try:
                val = hx.get_weight(5)
                print(val)
                self.y.append(val)
                self.x.append(self.verticalSlider.value())
                val=round(val,1)
                self.lcdNumber_3.display(str(val))
                hx.power_down()
                hx.power_up()
                time.sleep(0.1)
            except (KeyboardInterrupt, SystemExit):
                cleanAndExit()

    
        
        


    def plot_graph(self):
        pen = pg.mkPen('g',width=5)
        self.widget_2.setTitle('Thrust vs Throttle')
        self.widget_2.plot(self.x,self.y,pen=pen)
        
    

    def display_lcd(self):
        self.lcdNumber_2.display("120")
        
    def onStartButton_click(self):
        self.radioButton.toggled.connect(lambda: self.start_manual_motor(self.radioButton.isChecked()))
        self.radioButton_2.toggled.connect(lambda: self.start_automatic_motor(self.radioButton_2.isChecked()))
        
    def start_automatic_motor(self,selected):
        self.label_11.setText("ON")
        self.label_16.setText("I'm Starting the motor, I hope its calibrated and armed, if not click on calibrate motor button")
        print ("I'm Starting the motor, I hope its calibrated and armed, if not restart by giving 'x'")
        os.system ("sudo pigpiod")
        time.sleep(1)
        time.sleep(1)
        self.ESC=4
        self.pi = pigpio.pi();
        self.pi.set_servo_pulsewidth(self.ESC, 0) 
        self.max_value = 2000 #change this if your ESC's max value is different or leave it be
        self.min_value = 700
        self.speed=700
        self.pi.set_servo_pulsewidth(self.ESC, self.speed)
        EMULATE_HX711=False

        referenceUnit = 233016.888888889
        if not EMULATE_HX711:
            import RPi.GPIO as GPIO
            from hx711 import HX711
        else:
            from emulated_hx711 import HX711

        def cleanAndExit():
            print("Cleaning...")

            if not EMULATE_HX711:
                GPIO.cleanup()
        
            print("Bye!")
            sys.exit()

        hx = HX711(5, 6)
        hx.set_reading_format("MSB", "MSB")
        hx.set_reference_unit(referenceUnit)

        hx.reset()

        hx.tare()
        print("Tare done! Add weight now...")
        self.label_16.setText('Tare done')
        a=1168
        while(True):
            self.speed=a
            a=a+10
            val = hx.get_weight(5)
            print(val)
            self.y.append(val)
            self.x.append(self.verticalSlider.value())
            val=round(val,1)
            self.lcdNumber_3.display(str(val))
            hx.power_down()
            hx.power_up()
            time.sleep(0.5)
            print(a)
            if a>2200:
                self.label_16.setText("")
                self.label_11.setText("OFF")
                self.pi.set_servo_pulsewidth(self.ESC, 0)
                os.system ("sudo killall pigpiod")
                GPIO.cleanup()
                self.plot_graph()
                break
            
        
    def start_manual_motor(self,selected):
        self.t.start()
        self.label_11.setText("ON")
        self.label_16.setText("I'm Starting the motor, I hope its calibrated and armed, if not click on calibrate motor button")
        print ("I'm Starting the motor, I hope its calibrated and armed, if not restart by giving 'x'")
        os.system ("sudo pigpiod")
        time.sleep(1)
        time.sleep(1)
        self.ESC=4
        self.pi = pigpio.pi();
        self.pi.set_servo_pulsewidth(self.ESC, 0) 
        self.max_value = 2000 #change this if your ESC's max value is different or leave it be
        self.min_value = 700
        self.speed=1300
        self.verticalSlider.sliderPressed.connect(lambda: self.onSliderPressed())
        self.verticalSlider.valueChanged.connect(lambda: self.onValuechange())
        self.pushButton_4.clicked.connect(lambda: self.onStopButton_click())
        
        
    def onSliderPressed(self):
        self.pi.set_servo_pulsewidth(self.ESC, self.speed)
        
        print(self.speed)
    
    def onValuechange(self):
        def scale (num, in_min, in_max, out_min, out_max):
           return (num - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
        self.speed=scale(self.verticalSlider.value(),0,100,1168,2200)
        
        self.pi.set_servo_pulsewidth(self.ESC, self.speed)
        print(self.speed)
        
    def onStopButton_click(self):
        self.label_16.setText("")
        import RPi.GPIO as GPIO
        self.label_11.setText("OFF")
        self.pi.set_servo_pulsewidth(self.ESC, 0)
        os.system ("sudo killall pigpiod")
        GPIO.cleanup()
        self.plot_graph()
        
        
        
        
    def calibrate_motor(self):
        self.label_16.setText("Disconnect the battery...")
        os.system ("sudo pigpiod")
        time.sleep(1)
        time.sleep(1)
        self.ESC=4
        self.pi = pigpio.pi();
        self.pi.set_servo_pulsewidth(self.ESC, 0) 
        self.max_value = 2000 #change this if your ESC's max value is different or leave it be
        self.min_value = 700
        self.speed=700
        self.pi.set_servo_pulsewidth(self.ESC, 0)
        
        print("Disconnect the battery and press Enter")
        
        
        inp = input()
        if inp == '':
            self.pi.set_servo_pulsewidth(self.ESC, self.max_value)
            print("Connect the battery NOW.. you will here two beeps, then wait for a gradual falling tone then press Enter")
            self.label_16.setText("Connect the battery NOW.. you will here two beeps, then wait for a gradual falling tone then press Enter")
            inp = input()
            if inp == '':            
                self.pi.set_servo_pulsewidth(self.ESC, self.min_value)
                print ("Wierd eh! Special tone")
                self.label_16.setText("Wait for it ....")
                time.sleep(7)
                print ("Wait for it ....")
                time.sleep (5)
                print ("Im working on it, DONT WORRY JUST WAIT.....")
                self.pi.set_servo_pulsewidth(self.ESC, 0)
                time.sleep(2)
                print ("Arming ESC now...")
                self.pi.set_servo_pulsewidth(self.ESC, self.min_value)
                time.sleep(1)
                print ("See.... uhhhhh")
                self.label_16.setText("Calibration Done")
        


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Window()
    ui.show()
    sys.exit(app.exec_())