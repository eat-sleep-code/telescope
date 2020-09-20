# Telescope

This program is designed for the use of the Raspberry Pi HQ camera in long-exposure astrophotography situations.
   
---
## Getting Started

- Use [raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md) to:
  - Set the Memory Split value to a value of at least 192MB
  - Enable the CSI camera interface
  - Set up your WiFi connection
- Connect the Raspberry Pi HQ Camera to your Raspberry Pi


## Installation

Installation of the program, any software prerequisites, as well as DNG support can be completed with the following two-line install script.

```
wget -q https://raw.githubusercontent.com/eat-sleep-code/telescope/master/install-telescope.sh -O ~/install-telescope.sh
sudo chmod +x ~/install-telescope.sh && ~/install-telescope.sh
```

---

## Usage
```
telescope <options>
```

### Options

+ _--shutter_ : Set the shutter speed in milliseconds     *(default: 30000 milliseconds or 30 seconds)* 
+ _--iso_ : Set the ISO     *(default: 100)* 
+ _--duration_ :  Set the duration of the capture session in milliseconds    *(default: 3600000 milliseconds or 1 hour)* 
+ _--interval_ : Set the interval between captures in milliseconds    *(default: 500 milliseconds or &frac12; second)* 
+ _--outputFolder_ : Set the folder where images will be saved    *(default: dcim/)* 
+ _--raw_ : Set whether DNG files are created in addition to JPEG files    *(default: True)*
+ _--pixelCorrection_ : Set the defective pixel correction mode    *(default: 3)*
+ _--previewWidth_ : Set the preview window width     *(default: 800)*
+ _--previewHeight_ : Set the preview window height     *(default: 600)*


### Keyboard Controls
+ Press s+&#x25B2; or s+&#x25BC; to change shutter speed
+ Press i+&#x25B2; or i+&#x25B2; to change ISO
+ Press d+&#x25B2; or d+&#x25B2; to change the duration of the capture sequence in 1 minute increments
+ Press t+&#x25B2; or t+&#x25B2; to change the interval between captures in 1 second increments
+ Press [p] to toggle the preview window
+ Press [f] to toggle the preview window
+ Press the [space] bar to take photos or begin a timelapse
+ Press &#x241B; to exit

---

##  Speed of Operation

Due to the way the camera firmware works in low-light situations, several frames are captured *before* preview/focus windows are shown or capturing begins.  These operations my take 2-3 minutes *(or more)* to initialize.   Please be patient.

---

## Pixel Correction
The Raspberry Pi HQ camera includes built-in defective "hot" pixel correction (DPC).   DPC may result in faint stars being mistaken for defective pixels and removed from your image.   If you wish to disable the DPC, you max set the value accordingly at runtime by using the `--pixelCorrection` argument.   

|Value|Setting|
|---|---|
|0|All defective pixel corrections disabled|
|1|Mapped on-sensor defective pixel corrections enabled|
|2|Dynamic on-sensor defective pixel corrections enabled|
|3|Both mapped and dynamic on-sensor defective pixel corrections enabled *(default)*|

If you disable DPC, you will need to use dark frames in coordination with your stacking software to remove any "hot" pixels.

---

:information_source: *This application was developed using a Raspberry Pi HQ (2020) camera and Raspberry Pi 3B+ and Raspberry Pi 4B boards.   Issues will likely arise if you are using either third party or older hardware.*
