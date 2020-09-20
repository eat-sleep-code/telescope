from picamera import PiCamera
from pydng.core import RPICAM2DNG
import threading
import argparse
import datetime
import glob
import fractions
import keyboard
import os
import sys
import subprocess
import time


version = '2020.09.20'

camera = PiCamera()
camera.resolution = camera.MAX_RESOLUTION
PiCamera.CAPTURE_TIMEOUT = 1500
dng = RPICAM2DNG()


# === Argument Handling ========================================================

parser = argparse.ArgumentParser()
parser.add_argument('--shutter', dest='shutter', help='Set the shutter speed in milliseconds', type=int)
parser.add_argument('--iso', dest='iso', help='Set the ISO', type=int)
parser.add_argument('--duration', dest='duration', help='Set the duration of the capture session in milliseconds', type=int)
parser.add_argument('--interval', dest='interval', help='Set the interval between captures in milliseconds', type=int)
parser.add_argument('--outputFolder', dest='outputFolder', help='Set the folder where images will be saved', type=str)
parser.add_argument('--raw', dest='raw', help='Set whether DNG files are created in addition to JPEG files', type=bool)
parser.add_argument('--pixelCorrection', dest='pixelCorrection', help='Set the defective pixel correction mode', type=str)
parser.add_argument('--previewWidth', dest='previewWidth', help='Set the preview window width', type=int)
parser.add_argument('--previewHeight', dest='previewHeight', help='Set the preview window height', type=int)
args = parser.parse_args()


shutter = args.shutter or 30000    #(default: 30 seconds)
shutterLong = 30000
shutterShort = 0
defaultFramerate = 30
preFocusShutter = int(shutter)


iso = args.iso or 100
isoMin = 100
isoMax = 1600
preFocusIso = int(iso)


duration = args.duration or 3600000    #(default: 1 hour)
durationMin = shutter
durationMax = 86400000



interval = args.interval or 500    #(default: 1/2 second)
intervalMin = 500
intervalMax = 3600000


exposure = 'off'
preFocusExposure = exposure


awb = 'off'
preFocusAwb = awb


outputFolder = args.outputFolder or 'dcim/'
if outputFolder.endswith('/') == False:
	outputFolder = outputFolder+'/'


raw = args.raw or True


pixelCorrection = args.pixelCorrection    #(default: Enable mapped and dynamic on-sensor DPC)
if pixelCorrection == 'off' or pixelCorrection == 'False':
	pixelCorrection = 0
elif pixelCorrection == 'on' or pixelCorrection == 'True':
	pixelCorrection = 3
else:
	try:
		pixelCorrection = int(pixelCorrection)
	except:
		pixelCorrection = 3


previewVisible = False
try:
	previewWidth = args.previewWidth or 800
	previewWidth = int(previewWidth)
	previewHeight = args.previewHeight or 600
	previewHeight = int(previewHeight)
except: 
	previewWidth = 800
	previewHeight = 600


focusVisible = False

isCapturing = False


# === Echo Control =============================================================

def echoOff():
	subprocess.run(['stty', '-echo'], check=True)
def echoOn():
	subprocess.run(['stty', 'echo'], check=True)
def clear():
	subprocess.call('clear' if os.name == 'posix' else 'cls')
clear()


# === Functions ================================================================

def showInstructions(clearFirst = False, wait = 0):
	if clearFirst == True:
		clear()
	else:
		print('\n ----------------------------------------------------------------------\n ')

	print(' Press s+\u25B2 or s+\u25BC to change the shutter speed')
	print(' Press i+\u25B2 or i+\u25BC to change the ISO')
	print(' Press d+\u25B2 or d+\u25BC to change the duration of the capture sequence')
	print(' Press t+\u25B2 or t+\u25BC to change the interval between captures')
	print(' Press [p] to toggle the preview window')
	print(' Press [f] to toggle the focus window')
	print(' Press the [space] bar to take photos ')
	print(' Press \u241B to exit ')
	print('\n ----------------------------------------------------------------------\n ')
	time.sleep(wait)
	return

# ------------------------------------------------------------------------------

def setShutter(input, wait = 0):
	global shutter
	global shutterLong
	global shutterLongThreshold
	global shutterShort
	global defaultFramerate
	
	if str(input).lower() == 'auto' or str(input) == '0':
		shutter = 0
	else:
		shutter = int(float(input))
		if shutter < shutterShort:
			shutter = shutterShort
		elif shutter > shutterLong:
			shutter = shutterLong 

	try:
		camera.framerate=fractions.Fraction(5, 1000)
		
		if shutter == 0:
			camera.shutter_speed = 0
			# print(' DEBUG: ' + str(camera.shutter_speed) + ' | ' + str(camera.framerate) + ' | ' + str(shutter))	
			print(' Shutter Speed: auto')
		else:
			camera.shutter_speed = shutter * 1000
			# print(' DEBUG: ' + str(camera.shutter_speed) + ' | ' + str(camera.framerate) + ' | ' + str(shutter))		
			floatingShutter = float(shutter/1000)
			roundedShutter = '{:.3f}'.format(floatingShutter)
			print(' Shutter Speed: ' + str(roundedShutter) + 's')
		time.sleep(wait)
		return
	except Exception as ex:
		print(' WARNING: Invalid Shutter Speed!' + str(ex))


# ------------------------------------------------------------------------------				

def setISO(input, wait = 0):
	global iso
	global isoMin
	global isoMax
	if str(input).lower() == 'auto' or str(input) == '0':
		iso = 0
	else: 
		iso = int(input)
		if iso < isoMin:	
			iso = isoMin
		elif iso > isoMax:
			iso = isoMax	

	try:	
		camera.iso = iso
		# print(' DEBUG: ' + str(camera.iso) + ' | ' + str(iso))
		if iso == 0:
			print(' ISO: auto')
		else:	
			print(' ISO: ' + str(iso))
		time.sleep(wait)
		return
	except: 
		print(' WARNING: Invalid ISO Setting! ' + str(iso))

# ------------------------------------------------------------------------------				

def setDuration(input, wait = 0):
	global duration
	global durationMin
	global durationMax

	duration = int(input)
	if duration < durationMin:	
		duration = durationMin
	elif duration > durationMax:
		duration = durationMax	
	
	try:	
		floatingDuration = float(duration/1000)
		roundedDuration = '{:.3f}'.format(floatingDuration)
		print(' Duration: ' + str(roundedDuration)+ 's ')
		time.sleep(wait)
		return
	except: 
		print(' WARNING: Invalid Duration Setting! ' + str(duration))

# ------------------------------------------------------------------------------				

def setInterval(input, wait = 0):
	global interval
	global intervalMin
	global intervalMax

	interval = int(input)
	if interval < intervalMin:	
		interval = intervalMin
	elif interval > intervalMax:
		interval = intervalMax	
	
	try:	
		floatingInterval = float(interval/1000)
		roundedInterval = '{:.3f}'.format(floatingInterval)
		print(' Interval: ' + str(roundedInterval) + 's ')
		time.sleep(wait)
		return
	except: 
		print(' WARNING: Invalid Interval Setting! ' + str(interval))

# ------------------------------------------------------------------------------

def getFileName():
	now = datetime.datetime.now()
	datestamp = now.strftime('%Y%m%d')
	sequenceNumber = 1
	try:
		latestImagePath = max(glob.iglob(outputFolder + datestamp + '-*.jpg'),key=os.path.getmtime)
		sequenceNumber = int(latestImagePath.replace(outputFolder, '')[9:13]) + 1
	except:
		sequenceNumber = 1
		pass
	extension = '.jpg'
	return datestamp + '-' + str(sequenceNumber).zfill(4) + '-{counter:08d}' + extension

# ------------------------------------------------------------------------------

def getFilePath():
	try:
		os.makedirs(outputFolder, exist_ok = True)
	except OSError:
		print (' ERROR: Creation of the output folder ' + outputFolder + ' failed! ')
		echoOn()
		quit()
	else:
		return outputFolder + getFileName()

# ------------------------------------------------------------------------------

def showPreview(x = 0, y = 0, w = 800, h = 600):
	global previewVisible
	global focusVisible

	try:
		if focusVisible == True:
			focusVisible = False
			time.sleep(0.1)	
		
		previewWarmup = 120
		print('\n Initializing preview window.  Please wait ' + str(previewWarmup) + ' seconds...')	
		camera.start_preview(fullscreen=False, resolution=(w, h), window=(x, y, w, h))	
		previewVisible = True;
	except Exception as ex:
		print (' \n Error initializing preview window. ' + str(ex) )	
	time.sleep(0.1)
	return
	
# ------------------------------------------------------------------------------

def hidePreview():
	global previewVisible
	camera.stop_preview()
	previewVisible = False;
	time.sleep(0.1)
	return

# ------------------------------------------------------------------------------

def showFocus(x = 0, y = 0, w = 800, h = 600):
	global previewVisible
	global focusVisible
	global preFocusShutter
	global preFocusIso
	global preFocusExposure
	global preFocusAwb
	
	try:
		focusWarmup = 120
		print('\n Initializing focus window.  Please wait ' + str(focusWarmup) + ' seconds...')
		
		preFocusShutter = camera.shutter_speed
		preFocusIso = camera.iso
		preFocusExposure = camera.exposure_mode
		preFocusAwb = camera.awb_mode

		if previewVisible == True:
			previewVisible = False
			time.sleep(0.1)	

		camera.start_preview(fullscreen=False, resolution=(w, h), window=(x, y, w, h))	
		camera.zoom = (0, 0, 0.3, 0.2)
		focusVisible = True;
	except Exception as ex:
		print (' \n Error initializing focus window. ' + str(ex) )	
	time.sleep(0.1)	
	return
	
# ------------------------------------------------------------------------------

def hideFocus():
	global focusVisible
	camera.stop_preview()
	focusVisible = False;
	time.sleep(0.1)

	camera.shutter_speed = preFocusShutter
	camera.iso = preFocusIso
	camera.exposure_mode = preFocusExposure
	camera.awb_mode = preFocusAwb 
	camera.zoom = (0, 0, 0, 0)

	time.sleep(0.1)
	return

# ------------------------------------------------------------------------------

def resetPixelCorrection():
	global pixelCorrection
	if pixelCorrection != 3:
		try:
			print('\n INFO: Resetting pixel correction mode to default... \n' )
			subprocess.call('sudo vcdbg set imx477_dpc 3', stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=True)
		except Exception as ex:
			print(' WARNING: Unable to reset pixel correction. ' + str(ex))
			pass

# ------------------------------------------------------------------------------

def captureSequence(raw = True):
	captureWarmup = 120
	print('\n Starting capture.  Please wait ' + str(captureWarmup) + ' seconds... ')
	endTime = time.time() + int(duration / 1000)					
	for filename in camera.capture_continuous(getFilePath(), quality=100, bayer=raw):
		print(' INFO: Captured %s' % filename)
		if raw == True:
			conversionThread = threading.Thread(target=convertBayerDataToDNG, args=(filename,))
			conversionThread.start()
		if time.time() >= endTime:
			break

# ------------------------------------------------------------------------------		

def convertBayerDataToDNG(filepath):
	dng.convert(filepath)

# === Image Capture ============================================================

try:
	echoOff()
	imageCount = 1

	try:
		os.chdir('/home/pi') 
	except:
		pass
	
	def Capture(mode = 'persistent'):
		global previewVisible
		global previewWidth
		global previewHeight
		global shutter
		global shutterLong
		global shutterShort
		global iso
		global isoMin
		global isoMax
		global duration
		global durationMin
		global durationMax
		global interval
		global intervalMin
		global intervalMax
		global exposurei
		global ev
		global evMin
		global evMax
		global bracket
		global awb
		global timer
		global raw
		global pixelCorrection
		global imageCount
		global isCapturing

		# print(str(camera.resolution))
		camera.sensor_mode = 3

		print('\n Telescope ' + version )
		print('\n ----------------------------------------------------------------------\n')
		
		if pixelCorrection != 3:
			try:
				print(' Pixel Correction Mode: ' + str(pixelCorrection) )
				subprocess.call('sudo vcdbg set imx477_dpc ' + str(pixelCorrection), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=True)
			except:
				print(' WARNING: Unable to set pixel correction. ')
				pass

		setShutter(shutter, 0)		
		setISO(iso, 0)
		setDuration(duration, 0)
		setInterval(interval, 0)
		
		time.sleep(2)
		
		camera.exposure_mode = exposure
		gains = camera.awb_gains
		#camera.awb_mode = awb
		#camera.awb_gains = gains
		

		showInstructions(False, 0)
		# showPreview(0, 0, previewWidth, previewHeight)
		
		# print('Key Pressed: ' + keyboard.read_hotkey())
		while True:
			try:
				if keyboard.is_pressed('ctrl+c') or keyboard.is_pressed('esc'):
					# clear()
					isCapturing = False
					echoOn()
					break

				# Help
				elif keyboard.is_pressed('/') or keyboard.is_pressed('shift+/'):
					showInstructions(True, 0.5)	

				# Capture
				elif keyboard.is_pressed('space'):
					captureSequence(raw)
						

				# Preview Toggle				
				elif keyboard.is_pressed('p'):
					if previewVisible == True:
						hidePreview()
					else:
						showPreview(0, 0, previewWidth, previewHeight)
					time.sleep(1.0)

				# Focus Toggle				
				elif keyboard.is_pressed('f'):
					if focusVisible == True:
						hideFocus()
					else:
						showFocus(0, 0, previewWidth, previewHeight)
					time.sleep(1.0)

				# Shutter Speed	
				elif keyboard.is_pressed('s+up'):
					if shutter == 0:
						shutter = shutterShort
					if shutter > shutterShort and shutter <= shutterLong:					
						shutter = int(shutter / 1.5)
					setShutter(shutter, 0.25)
				elif keyboard.is_pressed('s+down'):
					if shutter == 0:						
						shutter = shutterLong
					elif shutter < shutterLong and shutter >= shutterShort:					
						shutter = int(shutter * 1.5)
					elif shutter == shutterShort:
						shutter = 0
					setShutter(shutter, 0.25)

				# ISO
				elif keyboard.is_pressed('i+up'):
					if iso == 0:
						iso = isoMin
					if iso >= isoMin and iso < isoMax:					
						iso = int(iso * 2)
					setISO(iso, 0.25)
				elif keyboard.is_pressed('i+down'):
					if iso == 0:
						iso = isoMax
					elif iso <= isoMax and iso > isoMin:					
						iso = int(iso / 2)
					elif iso == isoMin:
						iso = 0
					setISO(iso, 0.25)

				# Duration
				elif keyboard.is_pressed('d+up'):
					if duration >= durationMin and duration < durationMax:					
						duration = duration + 60000
					setDuration(duration, 0.25)
				elif keyboard.is_pressed('d+down'):
					if duration > durationMin and duration <= durationMax:					
						duration = duration - 60000
					setDuration(duration, 0.25)

				# Interval
				elif keyboard.is_pressed('t+up'):
					if interval >= intervalMin and interval < intervalMax:					
						interval = interval + 1000
					setInterval(interval, 0.25)
				elif keyboard.is_pressed('t+down'):
					if interval > intervalMin and interval <= intervalMax:					
						interval = interval - 1000
					setInterval(interval, 0.25)

			except Exception as ex:
				print(ex)
				pass


	Capture()

except KeyboardInterrupt:
	resetPixelCorrection()
	echoOn()
	sys.exit(1)
