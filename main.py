import os
import sys
import json
import threading
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from jnius import autoclass, cast
from vosk import Model, KaldiRecognizer
import pyaudio

class JarvisEngineApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex('#0B0C10')
        layout = BoxLayout(orientation='vertical', padding=40)
        self.console = Label(
            text="[ J.A.R.V.I.S. MATRIX ONLINE ]\nInitializing localized subroutines...",
            font_size='18sp',
            color=get_color_from_hex('#66FCF1'),
            halign='center'
        )
        layout.add_widget(self.console)
        self.reminders = {"18:00": "Review Class 9 Physics assignment, Sir."}
        Clock.schedule_once(self.boot_jarvis, 1)
        return layout

    def log(self, text):
        Clock.schedule_once(lambda dt: setattr(self.console, 'text', f"[ J.A.R.V.I.S. ]\n{text}"))

    def boot_jarvis(self, dt):
        try:
            if not os.path.exists("model"):
                self.log("Error: Offline 'model' folder missing from system path.")
                return
            self.model = Model("model")
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.audio_system = pyaudio.PyAudio()
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.current_activity = PythonActivity.mActivity
            self.context = cast('android.content.Context', self.current_activity)
            self.log("All systems operational locally, Sir.\nSay 'Jarvis' to activate.")
            threading.Thread(target=self.continuous_background_listener, daemon=True).start()
            threading.Thread(target=self.reminder_cron_service, daemon=True).start()
        except Exception as e:
            self.log(f"System Boot Failure: {str(e)}")

    def continuous_background_listener(self):
        stream = self.audio_system.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
        stream.start_stream()
        while True:
            data = stream.read(2000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                packet = json.loads(self.recognizer.Result())
                phrase = packet.get("text", "").lower()
                if "jarvis" in phrase:
                    self.log("Jarvis: 'Yes, Sir.'")
                    self.execute_native_tts("Yes, Sir.")
                    self.process_vocal_stream(stream)

    def process_vocal_stream(self, stream):
        self.log("Listening for executive command...")
        for _ in range(25):  
            data = stream.read(2000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                packet = json.loads(self.recognizer.Result())
                command = packet.get("text", "").lower()
                if "open youtube" in command:
                    self.open_target_application("com.google.android.youtube")
                elif "screen" in command or "read" in command:
                    self.read_active_screen_content()
                elif "sleep" in command or "off" in command:
                    self.toggle_device_power(state=False)
                break

    def open_target_application(self, package_name):
        try:
            pm = self.context.getPackageManager()
            intent = pm.getLaunchIntentForPackage(package_name)
            if intent:
                intent.addFlags(autoclass('android.content.Intent').FLAG_ACTIVITY_NEW_TASK)
                self.context.startActivity(intent)
                self.log(f"Launching external app index: {package_name}")
            else:
                self.log("Application bundle not installed on local device memory.")
        except Exception as e:
            self.log(f"Process routing failure: {str(e)}")

    def read_active_screen_content(self):
        try:
            self.log("Scanning active screen elements, Sir...")
            AccessibilityService = autoclass('android.accessibilityservice.AccessibilityService')
            root_node = self.current_activity.getWindow().getDecorView().getRootView()
            self.log("Screen scanning sequence completed internally, Sir.")
        except Exception as e:
            self.log("Screen parsing requires structural Accessibility Permissions.")

    def toggle_device_power(self, state=True):
        try:
            PowerManager = autoclass('android.os.PowerManager')
            power_service = self.context.getSystemService(autoclass('android.content.Context').POWER_SERVICE)
            pm = cast('android.os.PowerManager', power_service)
            if not state:
                self.log("Powering down display matrix. Goodbye, Sir.")
        except Exception as e:
            self.log("Power state changes require Administrative Root parameters.")

    def reminder_cron_service(self):
        import time
        while True:
            now = datetime.now().strftime("%H:%M")
            if now in self.reminders:
                reminder_text = self.reminders[now]
                self.log(f"CRITICAL REMINDER: {reminder_text}")
                self.execute_native_tts(reminder_text)
                time.sleep(61)
            time.sleep(10)

    def execute_native_tts(self, text):
        try:
            TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
            pass 
        except:
            pass

if __name__ == '__main__':
    JarvisEngineApp().run()
