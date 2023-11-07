import sys
from PyQt5.QtWidgets import QApplication
from screeninfo import get_monitors
import math

app = QApplication(sys.argv)
screen = app.screens()[0]
dpi = screen.physicalDotsPerInch()
app.quit()

def get_monitor_dimensions():
    monitors = get_monitors()
    if len(monitors) > 0:
        monitor = monitors[0]  # Get the primary monitor
        width = monitor.width
        height = monitor.height

        return (width/dpi)*2.54/100, (height/dpi)*2.54/100, dpi
    else:
        raise Exception("No monitors detected!")

width, height, dpi = get_monitor_dimensions()
print(f"Monitor Width: {width} m")
print(f"Monitor Height: {height} m")
print("MONITOR RESOLUTION IN INCHES: ", round(math.sqrt((width*100/2.54)**2 + (height*100/2.54)**2)))