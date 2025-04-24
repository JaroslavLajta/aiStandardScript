# aiStandardScript (Arnold Standard Surface importer for Maya 2025+)

*A tool that loads textures and creates an aiStandardSurface shader*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Features

- Automatic matching of files according to the naming in Maya
- Easily choose different color spaces for each texture
- Able to detect OpenGL and DirectX normal maps based on naming
- User can choose from different normal maps
- Script gives warnings about files that aren't suitable

## Installation

1. Download or clone this repository.
2. Copy the script file and JSON to your Maya scripts directory:  
```
Documents/maya/<version>/scripts/
```
3. In Maya, open the Script Editor and run:
```
import aiStandardScript as aiS
import imp

imp.reload(aiS)
```

## Usage

Your textures need to be named the same as they are called in Maya, in lowercase, with an underscore before.   
Exceptions are for Normal, Bump, and Height; everything else is named after Arnold in Maya.   
If the name is 3 words long, like: Transmission Extra Depth, the script expects _transmissionextradepth.   


yourtexture_specularrougness.png ----> Connects to Specular Roughness   
yourtexture_normal_directx.exr ----> Connects to Normal   
...


1. Click Select Directory
2. Choose the directory and press OK
3. Choose your colorspaces and normal type
4. Choose your name
5. Click Create Shader
6. Enjoy


## Requirements

- Autodesk Maya (version 2025+)
- Script and config JSON

## Credits

- Script by Jaroslav Lajta

## License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0)
