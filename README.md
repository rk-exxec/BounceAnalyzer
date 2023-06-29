# BounceAnalyzer

BounceAnalyzer provides a user friendly interface to analyze the bounces of round/spherical objects. Its designed with ease of use in mind and supports batch processing of entire folder structures.

Currently the following key parameters are extracted:
- Penetration depth
- Coefficient of restitution (Speed in divided by speed out)
- Maximum acceleration

Additionally the following parameters are analyzed:
- Distance of object
- Velocity of object
- Acceleration of object
- Size and pixel scale

BounceAnalyzer can load Photron High Speed Camera Videos (*.cihx, *.mraw) additionally to all other popular video formats, thanks to the [pyMRAW](https://github.com/ladisk/pyMRAW) library.

Data is exported as `.csv` and `.json`. The streak image is saved as png. The json file can be opened again to show all the evaluated data.

BounceAnalyzer can do batch processing on entire folders, simply drag a folder over the interface to open a pattern matching dialog.

## Installation

Uses Python 3.9.4 or higher  
Clone the repo, then execute `pip install -r requirements.txt` to install the required packages.

## Usage

Execute `python src/bounce_process.py`.



### Video Tab:
This tab contains video control elements, as well as evaluation parameters. 

To load a video, use the `File->Open` dialog, or drag and drop the *.cihx file onto the window. If no cihx file is available, the program can open normal mp4 files as well, however some functionality might be unavailable.

To process multiple file at once, use the `File->Batch Process` dialog, or drag and drop a folder onto the window.
This will open a pattern matching dialog for the filetype and -names which should be processed. (Default is `*.cihx`)
The results for each video will be stored in its source directory.

To process the video, simply press `Start Eval`.  
The bottom row contains also parameters for the evaluation:
- Acceleration Threshold: used to detect the contact of the object with the surface.
- Pixel Scale: Can be used to manually set the pixel scale, if not supplied by metadata. "Auto" will either pull from metadata or calculate from object diameter.
- Ball Size: Set the object diameter for calculation of pixel scale
- Relative Image Threshold: Used for edge detection. Relative to the maximum value in the video.

### Data Tab:

This tab displays the streak image, the detected position, velocity and acceleration of the object, as well as the extracted parameters, like coefficient of restitution, maximum penetration, maximum acceleration etc.

The buttons can be used to export the data to csv and json format.

### Raw Data Tab:

Contains all the measured values as table.

