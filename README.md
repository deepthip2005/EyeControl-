# EyeControl-
👁️ EyeControl — Hands-Free Computer Control Using Your Eyes

Control your entire computer — cursor, clicks, volume, brightness, and typing — using only your eyes and a webcam. No mouse. No keyboard. No special hardware.

🎯 What is EyeControl?
EyeControl is a real-time, gaze-based interaction system that lets you control your computer entirely through eye movement and blinks. Built with Python and powered by Google's MediaPipe Face Landmarker, it tracks your iris position through a standard webcam and translates your gaze into mouse movements, clicks, and system controls.
Designed as an accessibility tool for users with physical disabilities — and anyone curious about hands-free computing.

✨ Features
ActionHow to Do It🖱️ Move cursorLook where you want to go👆 Single clickBlink once👆👆 Double clickBlink twice quickly🔛 Toggle hands-free modeBlink 3 times🔊 Volume upLook at right screen edge (2 sec)🔇 Volume downLook at left screen edge (2 sec)☀️ Brightness upLook at top screen edge (2 sec)🌑 Brightness downLook at bottom screen edge (2 sec)⌨️ Type textUse the floating eye keyboard (dwell to select keys)

🧠 How It Works
Detection
MediaPipe's Face Landmarker model detects 478 facial landmarks per frame in real time, including precise iris landmarks. The Eye Aspect Ratio (EAR) is computed from eyelid landmarks to detect blinks:
EAR = (||p2-p6|| + ||p3-p5||) / (2 × ||p1-p4||)
A blink is registered when EAR drops below 0.22 for 2+ consecutive frames.
Calibration
On startup, a 5-point calibration routine maps your iris position to screen coordinates. You look at 5 dots (corners + centre) and blink once at each. A least-squares linear regression model is fitted to produce accurate screen-space predictions.
Cursor Smoothing
An exponential moving average (factor = 0.25) is applied to remove jitter from natural micro eye-movements, producing fluid cursor motion.

🏗️ Project Structure
EyeControl/
├── blink_test.py          # Main control engine
├── launcher.py            # Startup GUI launcher
├── face_landmarker.task   # MediaPipe face landmark model
├── EyeControl.spec        # PyInstaller build config
├── EyeControl.exe         # Standalone Windows executable
└── README.md

🚀 Getting Started
Option A — Run the Executable (Windows, No Setup Needed)

Download EyeControl.exe from the Releases page
Double-click to launch
Follow the on-screen calibration instructions
Blink 3 times to activate hands-free mode

Option B — Run from Source
Requirements

Python 3.8+
Webcam
Windows OS (volume control uses Windows Audio API)

Install dependencies
bashpip install opencv-python mediapipe pyautogui numpy keyboard screen-brightness-control pycaw comtypes
Run
bashpython launcher.py

📋 Usage Guide
Step 1 — Calibration
When the app starts, 5 red dots will appear one by one across your screen. Look directly at each dot and blink once to record that calibration point. This takes about 15 seconds.
Step 2 — Activate Hands-Free Mode
Blink 3 times rapidly to toggle hands-free mode ON. The status indicator in the webcam window will turn green.
Step 3 — Control Your Computer

Move your eyes to move the cursor
Blink once to click, twice to double-click
Look at screen edges for 2 seconds to adjust volume/brightness
The floating keyboard appears automatically — hover your gaze over a key for 0.6 seconds to type it

Step 4 — Exit
Press ESC or Q at any time to quit. Blink 3 times to toggle hands-free mode off without exiting.

⚙️ Tech Stack

Python — Core language
MediaPipe — Face & iris landmark detection
OpenCV — Webcam capture and frame processing
PyAutoGUI — Cursor movement and mouse simulation
NumPy — Calibration regression
Tkinter — Floating keyboard UI & launcher
pycaw — Windows volume control
screen-brightness-control — Display brightness


🔧 Building the Executable
To rebuild the .exe from source using PyInstaller:
bashpip install pyinstaller
pyinstaller EyeControl.spec
The output will be in the dist/ folder.

⚠️ Known Limitations

Head movement — Accuracy drops if you move your head significantly after calibration. Recalibrate if needed.
Lighting — Works best in well-lit, even lighting. Harsh backlighting or darkness may affect landmark detection.
Windows only — Volume control uses the Windows Core Audio API. macOS/Linux support is partial.
Single user — Calibration is per-session and per-user. Each user should recalibrate.


🔮 Planned Features

 Head-pose compensation for post-calibration movement
 Polynomial regression calibration for higher accuracy
 Per-user adaptive EAR threshold
 Right-click via sustained wink
 Scroll gesture support
 Word prediction in floating keyboard
 macOS / Linux support


📄 License
This project is open source and available under the MIT License.

🙋 Author
Built by Deepthi
Feel free to open an issue or pull request for suggestions and improvements.


"Accessibility should be the default, not the exception."
