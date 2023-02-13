import sys
import os
import random
import datetime as dt
import requests
import json
from PyQt6.QtCore import QRect, QSize, QTimer, Qt
from PyQt6.QtGui import QAction, QIcon, QPixmap, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QPushButton, QWidget

from PIL import Image
from PIL.ImageQt import ImageQt

FONT = "Arial"

# dialogs

class CloseDialog(QDialog):
    def __init__(self, master):
        super().__init__(master)
        self.setGeometry(QRect(1000, 1000, 420, 80))

        self.setWindowTitle("Benden")
        message = QLabel(parent= self,text="Möchten Sie das System herunterfahren?")
        message.setGeometry(QRect(85, 10, 250, 25))

        self.exit_button = QPushButton(parent= self,text="Beenden")
        self.exit_button.setGeometry(QRect(10, 45, 100, 25))
        self.exit_button.clicked.connect(lambda: master.close())
        
        self.restart_button = QPushButton(parent= self,text="Neustart")
        self.restart_button.setGeometry(QRect(110, 45, 100, 25))
        self.restart_button.clicked.connect(self.restsart_system)
        
        self.cancel_button = QPushButton(parent= self,text="Abbrechen")
        self.cancel_button.setGeometry(QRect(210, 45, 100, 25))
        self.cancel_button.clicked.connect(self.close)
        
        self.shutdown_button = QPushButton(parent= self,text="Ausschalten")
        self.shutdown_button.setStyleSheet("background-color : red")
        self.shutdown_button.setGeometry(QRect(310, 45, 100, 25))
        self.shutdown_button.clicked.connect(self.shutdown_system)

    def restsart_system(self):
        print("neustart")
    def shutdown_system(self):
        print("herunterfahren")    

# widgets

class DiaWidget(QWidget):
    def __init__(self, master):
        super().__init__(master)
        
        self.setGeometry(QRect(0, 20, master.width(), 550))
        
        self.dia = DiaLabel(self)
        
        self.datetime_widget = DateTimeWidget(self)
        
        self.weather_widget = WeatherWidget(self)

class WeatherWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.path = "gui/icons/weather_icons/"
        self._width = 370
        
        self._height = 100
        
        self.setGeometry(QRect(parent.width()-self._width-30,
                               parent.height()-self._height, 
                               self._width, 
                               self._height))
        
        
        self.sunrise_icon = IconLabel(self,f"{self.path}sunrise.png",0,60,25,25)
        self.sunriselabel = QLabel(" ",self)
        self.sunriselabel.setFont(QFont(FONT,15,50))
        self.sunriselabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.sunriselabel.setGeometry(QRect(27,62,60,20))
        
        self.sunset_icon = IconLabel(self,f"{self.path}sunset.png",82,60,25,25)
        self.sunsetlabel = QLabel(" ",self)
        self.sunsetlabel.setFont(QFont(FONT,15,50))
        self.sunsetlabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.sunsetlabel.setGeometry(QRect(110,62,60,20))
        
        self.curr_icon = QLabel(" ",self)
        self.curr_icon.setGeometry(QRect(self._width-190,10,80,80))
        
        self.templabel = QLabel(" ",self)
        self.templabel.setFont(QFont(FONT,25,50))
        self.templabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.templabel.setGeometry(QRect(self._width-80,0,80,30))
        
        self.feellabel = QLabel(" ",self)
        self.feellabel.setFont(QFont(FONT,15,50))
        self.feellabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.feellabel.setGeometry(QRect(self._width-80,35,80,20))
        
        self.windlabel = QLabel(" ",self)
        self.windlabel.setFont(QFont(FONT,15,50))
        self.windlabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.windlabel.setGeometry(QRect(self._width-80,60,80,20))
        
        self.wind_icon = IconLabel(self,f"{self.path}wind.png",self._width-100,60,20,20)       

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(3600000)
        
        self.update()
        
    def get_forecast(self):
        with open("personal.json","r") as pd:
            data = json.load(pd)
            api_key = data["openweather-api-key"]
        
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat=52.517471&lon=13.463824&appid={api_key}&units=metric"
        response = requests.get(url)
        
        if response.ok:
            data = json.loads(response.text)
            with open("temp/weather-forecast.json","w") as wf:
                json.dump(data, wf, indent=4)

        else:                                            # ToDo -> else / exception eg data = None
            with open("temp/weather-forecast.json","r") as wf:
                data = json.load(wf)
        
        return data        

    def update(self):
        
        self.forecast_data = self.get_forecast() # ToDo if response != 200 -> warning
        
        sunrise = self.forecast_data["current"]["sunrise"]
        sunrise = dt.datetime.fromtimestamp(sunrise).strftime("%H:%M")
        self.sunriselabel.setText(sunrise)
        
        sunset = self.forecast_data["current"]["sunset"]
        sunset = dt.datetime.fromtimestamp(sunset).strftime("%H:%M")
        self.sunsetlabel.setText(sunset)
        
        temp = self.forecast_data["current"]["temp"]
        temp = f"{round(temp)} °C"
        self.templabel.setText(temp)
        
        
        feel = self.forecast_data["current"]["feels_like"]
        feel = f"{round(feel)} °C"
        self.feellabel.setText(feel)
        
        
        wind = self.forecast_data["current"]["wind_speed"]
        wind = f"{round(wind)} km/h"
        self.windlabel.setText(wind)
        
        curr_icon = self.forecast_data["current"]["weather"][0]["icon"]
        icon_path = f"{self.path}{curr_icon}@2x.png"
        curr_icon = QPixmap(icon_path)
        self.curr_icon.setPixmap(curr_icon)
        self.curr_icon.setScaledContents(True)

class DateTimeWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self._width = 200
        self._height = 100
        
        self.setGeometry(QRect(20, 
                               parent.height()-self._height, 
                               self._width, 
                               self._height))
        
        self.timelabel = QLabel(" ",self)
        self.timelabel.setFont(QFont(FONT,60,50))
        self.timelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timelabel.setGeometry(QRect(0, 0, 200, 80))
        
        self.datelabel = QLabel(" ",self)
        self.datelabel.setFont(QFont(FONT,22,50))
        self.datelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.datelabel.setGeometry(QRect(0, 80, 200, 20))

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(500)

        self.update()

    def update(self):
        now = dt.datetime.now()
        time = now.time().strftime("%H:%M")
        date = now.date().strftime("%a %d.%m.%Y")
        self.timelabel.setText(time)
        self.datelabel.setText(date)

# Label

class IconLabel(QLabel):
    def __init__(self, parent, path:str , x_pos, y_pos, width, height):
        super().__init__(parent)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self._width = width
        self._height = height
        
        wind_icon = QPixmap(path)
        self.setPixmap(wind_icon)
        self.setScaledContents(True)
        self.setGeometry(QRect(self.x_pos, self.y_pos, self._width, self._height))    

class DiaLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(parent.width(),parent.height())
        
        self.path = "data/dia/calendar_wallpaper/"

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(300000)

        self.update()

    def update(self):
        album = os.listdir(self.path)
        
        i = random.randint(0,len(album)-1)        
        
        self.image = Image.open(f"{self.path}{album[i]}")
        self.image = self.adjust_imagesize(self.image, (self.width(),self.height()))
        self.image = self.add_gradient(self.image)
        self.setPixmap(self.image)
    
    @staticmethod
    def adjust_imagesize(img, widgt_size):
        
        widgt_width , widgt_height = widgt_size
        img_width , img_height = img.size
        target_width = int(img_width * img_height / img_width) # ratio = img_height / img_width
        
        img = img.resize((target_width, widgt_height))
        
        offcut = int((target_width - widgt_width) / 2)
        cutout = (offcut, 0, target_width - offcut, widgt_height)
        img_cutout = img.crop(cutout)
        
        return img_cutout
    
    @staticmethod
    def add_gradient(img):
            
        width , height = img.size
        # convert in RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        # draw transparent gradient
        gradient = Image.new('L', (1,height))
        for y in range(height):
            gradient.putpixel((0,(height-1)-y),int(y*0.7))   
        gradient = gradient.resize(img.size)
        
        img.putalpha(gradient)
        image = QPixmap.fromImage(ImageQt(img))

        return image
        

if __name__ == "__main__":

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setFixedSize(900,1650)

            dia = DiaWidget(self)

        def update(self):
            print("update 1")

    app = QApplication(sys.argv)
    
    w = MainWindow()
    w.show()
    app.exec()
