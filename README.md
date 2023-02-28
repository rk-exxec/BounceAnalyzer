# BounceAnalyzer

BounceAnalyzer provides a user friendly interface to analyse the bounces of round/spherical objects. Its designed with ease of use in mind and supports batch processing of entire folder structures.

Currently the following key paramters are extracted:
- Penetration depth
- Coefficient of restitution (Speed in divided by speed out)
- Maximum acceleration

Additionally the following parameters are analyzed:
- Distance of object
- Velocity of object
- Acceleration of object
- Size and pixel scale

BounceAnalyzer can load Photron High Speed Camera Videos (*.cihx, *.mraw) additionally to all other popular video formats, thanks to the [pyMRAW](https://github.com/ladisk/pyMRAW) library.

Data is exported as `.csv`.

BounceAnalyzer can do batch processing on entire folders
