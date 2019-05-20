# Pi Duet Wifi Neopixel (PDWN)

_PDWN is used to set and change the display of the neo-pixel rings on the BLV mln printer. For example, you could set a ring to display bed temperature while it is heating (idle) then display print percent while it is printing, and flash a rainbow when the print is done._

Here are some of the reasons I wrote PDWL:
* Connects to your network via WiFi, so no serial connection to Duet needed
  * PDWN communicates with Duet using http requests to get status reports from the printer
* Runs on Raspberry Pi Zero W which is inexpensive and very versatile, AND easily programmed with python
* Communicates with neo-pixel rings via a single PWM pin on the GPIO using Adafruit CircuitPython Neopixel library
  * Uses direct memory access, hence no reliance on CPU - can be used on devices like Raspberry Pi
* Serves web interface GUI so neo-pixel rings can be assigned/changed from any computer/phone/device on your network
* Rings can display different information for different states reported by the printer
* Ring displays/states can easily be changed on-the-fly any time you change your mind
* Foreground/background colors can easily be set using GUI
* PDWN can (potentially) easily be upgraded in the future to support handling other actions besides ring display.
  Examples:
  * Sending text(s) with print percentage or various printer states
  * Supporting attached webcam/timelapse usage
  * GUI for setting/changing front-panel pushbutton actions (sending G-Code via button press, etc.)

## How To Use
**NOTE: This is still under construction - not yet ready for distribution/use**

### Hardware/Wiring
This is what I had/used:  
[Raspberry Pi Zero W (with headers)](https://www.adafruit.com/product/3708)  
MicroSD card  
[Adafruit Perma Proto Bonnet](https://www.adafruit.com/product/3203)  
[Terminal block (good for external power to pi)](https://www.adafruit.com/product/724)  
Level-shifter such as [this one](https://www.adafruit.com/product/735)  

--Insert wiring diagram here--  
[See here for other wiring examples...](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring)


### Software
Here are the steps I took to start from scratch on a Raspberry Pi Zero W. As with everything raspberry pi, this installation requires quite a bit of terminal work and might not be for the faint of heart.

**NOTE: _This is in the early stages of development, and I have ONLY tested on a Raspberry Pi Zero W with the following versions._**  
Raspbian Stretch Lite vApril 2019  
Python 3.7.3  

#### Pi Initial setup and CircuitPython installation
* (Optional) Start reading here: https://learn.adafruit.com/circuitpython-on-raspberrypi-linux
* Follow the excellent quick-start steps 1 through 9 in the "Installing CircuitPython Libraries on Raspberry Pi" section called Prerequisite Pi Setup! [https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi]
* (Optional) Give your pi a recognizable name using sudo raspi-config
* (Optional?) Stretch comes with Python 3.5. I installed and compiled 3.7.3. Using 3.5 is untested.
  * Follow directions here for installing 3.7.3 [https://www.scivision.dev/compile-install-python-beta-raspberry-pi/]
  * Note: I had to use the following steps to increase the virtual memory in order to compile:
  * `sudo nano /etc/dphys-swapfile`
  * Change to CONF_SWAPSIZE=1024
  * Restart the service:
  * `sudo /etc/init.d/dphys-swapfile stop`
  * `sudo /etc/init.d/dphys-swapfile start`
  * Verify using `free -m`
* Continue CircuitPython instructions from above (**Update Your Pi and Python**, **Enable I2C and SPI**, **Install Python libraries**) all the way down through installing adafruit_blinka. You won't need to create the test file unless you'd like to experiment with controlling your neo-pixels.
* Use the following command from a terminal to install rpi_ws281x and the neopixel library:
  * `sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel`

#### PDWN installation
* Clone the PDL library from git:
  * `git clone https://github.com/barskey/DuetWifiLed.git`
* -- Insert python auto-start setup instructions here --
* Open a browser from your computer or phone and go to http://192.128.x.x or http://raspberrypi.local (or whatever name you assigned above .local)
* From the Settings tab, enter the IP address of your DuetWifi (note, duettest.local did not work for me. I had to use the actual IP address)
