Build for deployment with pyinstaller. First, figure out where libs are stored with

```shell
pip show customtkinter # copy Location: <customtkinter_dir>
```
It will show something like
```
Name: customtkinter
Version: 5.1.3
Summary: Create modern looking GUIs with Python
Home-page: https://customtkinter.tomschimansky.com
Author: Tom Schimansky
Author-email:
License: Creative Commons Zero v1.0 Universal
Location: C:\git\whispe-vosk\venv\Lib\site-packages
Requires: darkdetect
Required-by:
```
and you want to copy the location field. 

Using it, run the following to build the app on and for Windows environment:
```shell
pyinstaller --onedir --windowed --add-data "<location>/customtkinter;customtkinter/" --add-data "<location>/PvRecorder;PvRecorder/" --add-data "<location>/vosk;vosk/" app.py
```

To build it on and for Linux, run the following command, replacing `<location>` with actual value:
```shell
pyinstaller --onedir --windowed --add-data "<location>/customtkinter:customtkinter/" --add-data "<location>/pvrecorder:PvRecorder/" --add-data "<location>/vosk:vosk/" app.py --collect-all customtkinter --collect-all pvrecorder --collect-all vosk
```

So, examples for running on Windows and Linux are:
```shell
pyinstaller --onedir --windowed --add-data "C:\git\whispe-vosk\venv\Lib\site-packages/customtkinter;customtkinter/" --add-data "C:\git\whispe-vosk\venv\Lib\site-packages/PvRecorder;PvRecorder/" --add-data "C:\git\whispe-vosk\venv\Lib\site-packages/vosk;vosk/" app.py
pyinstaller --onedir --windowed --add-data "/home/chardash/git/whispe-vosk/venv/lib/python3.8/site-packages/customtkinter:customtkinter/" --add-data "/home/chardash/git/whispe-vosk/venv/lib/python3.8/site-packages/pvrecorder:PvRecorder/" --add-data "/home/chardash/git/whispe-vosk/venv/lib/python3.8/site-packages/vosk:vosk/" app.py --collect-all customtkinter --collect-all pvrecorder --collect-all vosk
```

The app will be available in `dist/app/app.exe`.
