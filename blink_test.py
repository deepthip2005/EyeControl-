import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
import tkinter as tk
import keyboard
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

model_path = "face_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_IRIS = [474, 475, 476, 477]

try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
    vol_range = volume_ctrl.GetVolumeRange()
    min_vol, max_vol = vol_range[0], vol_range[1]
    volume_available = True
except:
    try:
        from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
        speakers = AudioUtilities.GetSpeakers()
        speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_available = False
    except:
        volume_available = False
        print("Volume control not available on this device, skipping.")

def change_volume(direction):
    if not volume_available:
        pyautogui.press('volumeup' if direction == 'up' else 'volumedown')
        return
    cur_vol = volume_ctrl.GetMasterVolumeLevel()
    if direction == 'up':
        volume_ctrl.SetMasterVolumeLevel(min(cur_vol + 2, max_vol), None)
    else:
        volume_ctrl.SetMasterVolumeLevel(max(cur_vol - 2, min_vol), None)

def change_brightness(direction):
    try:
        cur = sbc.get_brightness()[0]
        if direction == 'up':
            sbc.set_brightness(min(cur + 10, 100))
        else:
            sbc.set_brightness(max(cur - 10, 10))
    except:
        pass

def eye_aspect_ratio(landmarks, eye_indices, w, h):
    points = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in eye_indices]
    vertical1 = abs(points[1][1] - points[5][1])
    vertical2 = abs(points[2][1] - points[4][1])
    horizontal = abs(points[0][0] - points[3][0])
    return (vertical1 + vertical2) / (2.0 * horizontal)

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    num_faces=1
)

screen_w, screen_h = pyautogui.size()
pyautogui.FAILSAFE = False

EDGE = 60
EDGE_DWELL = 2.0

KEYS = [
    ['Q','W','E','R','T','Y','U','I','O','P'],
    ['A','S','D','F','G','H','J','K','L'],
    ['Z','X','C','V','B','N','M','SPACE','DEL']
]

KEY_W = 65
KEY_H = 60
DWELL_TIME = 0.6

class FloatingKeyboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("EyeKeyboard")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.88)
        self.root.geometry(f"+{screen_w//2 - 340}+{screen_h - 280}")
        self.root.configure(bg='#111111')
        self.root.protocol("WM_DELETE_WINDOW", self.hide)
        self.buttons = {}
        self.visible = False

        for r, row in enumerate(KEYS):
            for c, key in enumerate(row):
                btn = tk.Label(self.root, text=key,
                               width=5 if key in ['SPACE','DEL'] else 3,
                               height=2, bg='#2a2a2a', fg='white',
                               font=('Arial', 12, 'bold'), relief='raised', bd=2)
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[key] = btn

        self.root.withdraw()

    def show(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.visible = True

    def hide(self):
        self.root.withdraw()
        self.visible = False

    def highlight(self, key, progress):
        if key in self.buttons:
            green = int(200 * progress)
            self.buttons[key].configure(bg=f'#00{green:02x}00')

    def reset_all(self):
        for key in self.buttons:
            self.buttons[key].configure(bg='#2a2a2a')

    def update(self):
        try:
            self.root.update()
        except:
            pass

    def exists(self):
        try:
            return self.root.winfo_exists()
        except:
            return False

keyboard_ui = FloatingKeyboard()
cap = cv2.VideoCapture(0)

CALIBRATION_POINTS = [
    (0.1, 0.1), (0.9, 0.1),
    (0.5, 0.5),
    (0.1, 0.9), (0.9, 0.9)
]

eye_points = []
screen_points = []

print("CALIBRATION: Look at each red dot and blink once.")

def collect_iris(landmarker, cap, w, h):
    samples = []
    start = time.time()
    while time.time() - start < 1.5:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = landmarker.detect(mp_image)
        if result.face_landmarks:
            lm = result.face_landmarks[0]
            samples.append((lm[LEFT_IRIS[0]].x, lm[LEFT_IRIS[0]].y))
    return np.mean(samples, axis=0) if samples else None

with FaceLandmarker.create_from_options(options) as landmarker:
    for i, (px, py) in enumerate(CALIBRATION_POINTS):
        sx = int(px * screen_w)
        sy = int(py * screen_h)
        blank = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)
        cv2.circle(blank, (sx, sy), 25, (0, 0, 255), -1)
        cv2.circle(blank, (sx, sy), 8, (255, 255, 255), -1)
        cv2.putText(blank, f"Look at the dot and BLINK ({i+1}/5)",
                    (screen_w//2 - 280, screen_h//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2)
        cv2.namedWindow("Calibration", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Calibration", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Calibration", blank)
        cv2.waitKey(1)

        frame_counter = 0
        eye_closed = False
        waiting = True

        while waiting:
            ret, frame = cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = landmarker.detect(mp_image)
            if result.face_landmarks:
                lm = result.face_landmarks[0]
                avg_ear = (eye_aspect_ratio(lm, LEFT_EYE, w, h) +
                           eye_aspect_ratio(lm, RIGHT_EYE, w, h)) / 2
                if avg_ear < 0.22:
                    frame_counter += 1
                    eye_closed = True
                else:
                    if eye_closed and frame_counter >= 2:
                        iris = collect_iris(landmarker, cap, w, h)
                        if iris is not None:
                            eye_points.append(iris)
                            screen_points.append((px, py))
                            print(f"Point {i+1} recorded!")
                            waiting = False
                    eye_closed = False
                    frame_counter = 0
            cv2.waitKey(1)

    cv2.destroyAllWindows()

    eye_points = np.array(eye_points)
    screen_points = np.array(screen_points)
    from numpy.linalg import lstsq
    A = np.column_stack([eye_points[:,0], eye_points[:,1], np.ones(len(eye_points))])
    cx, _, _, _ = lstsq(A, screen_points[:,0], rcond=None)
    cy, _, _, _ = lstsq(A, screen_points[:,1], rcond=None)

    print("Calibration done!")
    print("Blink 3 times = Hands-free ON/OFF")
    print("Single blink = Click | Double blink = Double click")
    print("Look at screen edges = Volume/Brightness")
    print("ESC or Q = quit anytime")
    time.sleep(1)

    smooth_x, smooth_y = screen_w // 2, screen_h // 2
    SMOOTH = 0.25
    EAR_THRESHOLD = 0.22
    BLINK_CONSEC_FRAMES = 2
    BLINK_WINDOW = 1.5

    hands_free = False
    blink_times = []
    frame_counter = 0
    eye_closed = False
    avg_ear = 0.3
    dwell_key = None
    dwell_start = None
    edge_zone = None
    edge_start = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if keyboard.is_pressed('esc') or keyboard.is_pressed('q'):
            break

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = landmarker.detect(mp_image)

        action = ""

        if result.face_landmarks:
            landmarks = result.face_landmarks[0]
            left_ear = eye_aspect_ratio(landmarks, LEFT_EYE, w, h)
            right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE, w, h)
            avg_ear = (left_ear + right_ear) / 2

            if avg_ear < EAR_THRESHOLD:
                frame_counter += 1
                eye_closed = True
            else:
                if eye_closed and frame_counter >= BLINK_CONSEC_FRAMES:
                    now = time.time()
                    blink_times.append(now)
                    blink_times = [t for t in blink_times if now - t <= BLINK_WINDOW]
                eye_closed = False
                frame_counter = 0

            now = time.time()
            recent = [t for t in blink_times if now - t <= BLINK_WINDOW]

            if len(recent) >= 3 and now - recent[-1] > 0.6:
                hands_free = not hands_free
                if hands_free:
                    action = "HANDS-FREE ON"
                    keyboard_ui.show()
                else:
                    action = "HANDS-FREE OFF"
                    keyboard_ui.hide()
                    keyboard_ui.reset_all()
                    dwell_key = None
                blink_times = []

            elif len(recent) == 2 and now - recent[-1] > 0.6:
                if hands_free:
                    pyautogui.doubleClick()
                    action = "DOUBLE CLICK"
                blink_times = []

            elif len(recent) == 1 and now - recent[-1] > 0.6:
                if hands_free:
                    pyautogui.click()
                    action = "SINGLE CLICK"
                blink_times = []

            if hands_free:
                ix = landmarks[LEFT_IRIS[0]].x
                iy = landmarks[LEFT_IRIS[0]].y
                pred_x = cx[0]*ix + cx[1]*iy + cx[2]
                pred_y = cy[0]*ix + cy[1]*iy + cy[2]
                target_x = int(pred_x * screen_w)
                target_y = int(pred_y * screen_h)
                target_x = max(0, min(screen_w-1, target_x))
                target_y = max(0, min(screen_h-1, target_y))
                smooth_x = int(smooth_x + (target_x - smooth_x) * SMOOTH)
                smooth_y = int(smooth_y + (target_y - smooth_y) * SMOOTH)
                pyautogui.moveTo(smooth_x, smooth_y)

                current_zone = None
                if smooth_x < EDGE:
                    current_zone = "VOL_DOWN"
                elif smooth_x > screen_w - EDGE:
                    current_zone = "VOL_UP"
                elif smooth_y < EDGE:
                    current_zone = "BRIGHT_UP"
                elif smooth_y > screen_h - EDGE:
                    current_zone = "BRIGHT_DOWN"

                if current_zone:
                    if current_zone == edge_zone:
                        elapsed = time.time() - edge_start
                        if elapsed >= EDGE_DWELL:
                            if current_zone == "VOL_UP":
                                change_volume('up')
                                action = "VOLUME UP"
                            elif current_zone == "VOL_DOWN":
                                change_volume('down')
                                action = "VOLUME DOWN"
                            elif current_zone == "BRIGHT_UP":
                                change_brightness('up')
                                action = "BRIGHTNESS UP"
                            elif current_zone == "BRIGHT_DOWN":
                                change_brightness('down')
                                action = "BRIGHTNESS DOWN"
                            edge_start = time.time()
                    else:
                        edge_zone = current_zone
                        edge_start = time.time()
                else:
                    edge_zone = None
                    edge_start = None

                if keyboard_ui.visible and keyboard_ui.exists():
                    kb_x = keyboard_ui.root.winfo_x()
                    kb_y = keyboard_ui.root.winfo_y()
                    rel_x = smooth_x - kb_x
                    rel_y = smooth_y - kb_y

                    hovered_key = None
                    for r, row in enumerate(KEYS):
                        for c, key in enumerate(row):
                            kx = c * (KEY_W - 10)
                            ky = r * (KEY_H - 5)
                            kw = KEY_W * 2 if key in ['SPACE', 'DEL'] else KEY_W
                            if kx <= rel_x <= kx + kw and ky <= rel_y <= ky + KEY_H:
                                hovered_key = key

                    if hovered_key:
                        if hovered_key == dwell_key:
                            elapsed = time.time() - dwell_start
                            progress = min(elapsed / DWELL_TIME, 1.0)
                            keyboard_ui.highlight(hovered_key, progress)
                            if elapsed >= DWELL_TIME:
                                if hovered_key == 'SPACE':
                                    pyautogui.press('space')
                                elif hovered_key == 'DEL':
                                    pyautogui.press('backspace')
                                else:
                                    pyautogui.typewrite(hovered_key.lower())
                                action = f"TYPED: {hovered_key}"
                                keyboard_ui.reset_all()
                                dwell_key = None
                                dwell_start = None
                                time.sleep(0.4)
                        else:
                            keyboard_ui.reset_all()
                            dwell_key = hovered_key
                            dwell_start = time.time()
                    else:
                        keyboard_ui.reset_all()
                        dwell_key = None
                        dwell_start = None

        mode_text = "HANDS-FREE ON  |  ESC = quit" if hands_free else "HANDS-FREE OFF  |  ESC = quit"
        color = (0, 255, 0) if hands_free else (0, 0, 255)
        cv2.putText(frame, mode_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, f"EAR: {avg_ear:.2f}", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        if action:
            print(action)
            cv2.putText(frame, action, (30, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.line(frame, (0, EDGE), (w, EDGE), (100, 100, 255), 1)
        cv2.line(frame, (0, h-EDGE), (w, h-EDGE), (100, 100, 255), 1)
        cv2.line(frame, (EDGE, 0), (EDGE, h), (100, 100, 255), 1)
        cv2.line(frame, (w-EDGE, 0), (w-EDGE, h), (100, 100, 255), 1)

        keyboard_ui.update()

        cv2.imshow("EyeControl", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
try:
    keyboard_ui.root.destroy()
except:
    pass

print("EyeControl exited cleanly.")






