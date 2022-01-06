import wave
import gpiozero
import pyaudio
import subprocess
import os
import sys
import queue


form_1 = pyaudio.paInt16  # 16-bit resolution
chans = 1  # 1 channel
samp_rate = 48000  # default value for the fifine mic
chunk = 4096  # 2^12 samples for buffer
record_secs = 5  # seconds to record
dev_index = 1  # device index found by p.get_device_info_by_index(ii)
wav_output_filename = '/home/pi/sound_project/test1.wav'  # name of .wav file

BUTTON1_GPIO = 1
BUTTON2_GPIO = 2
BUTTON3_GPIO = 3
BUTTON4_GPIO = 4
GPIO_LIST = [BUTTON1_GPIO, BUTTON2_GPIO, BUTTON3_GPIO, BUTTON4_GPIO]
INVALID_BUTTON = -1

RECORD_GPIO = 5


def open_audio():
    audio = pyaudio.PyAudio()  # create pyaudio instantiation
    stream = audio.open(format=form_1, rate=samp_rate, channels=chans,
                        input_device_index=dev_index, input=True,
                        frames_per_buffer=chunk)
    print("recording")
    return audio, stream


def close_audio(audio, stream):
    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()


class Buttons:
    def __init__(self, gpio, filename):
        self.gpio = gpio
        self.filename = filename
        self.button = gpiozero.Button(gpio)

    def record(self):
        audio, stream = open_audio()
        frames = []

        # loop through stream and append audio chunks to frame array
        # for ii in range(0, int((samp_rate / chunk) * record_secs)):
        while self.button.is_pressed:
            data = stream.read(chunk)
            frames.append(data)
        print("finished recording")

        close_audio(audio, stream)
        self.save_file(audio, frames)

    def save_file(self, audio, frames):
        # save the audio frames as .wav file
        wavefile = wave.open(self.filename, 'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()

    def play_file(self):
        print("Replaying")
        os.system("omxplayer -o local " + self.filename)
        print("Done")


buttons = []
for i in range(len(GPIO_LIST)):
    buttons.append(Buttons(GPIO_LIST[i], "/home/pi/sound_project/button"+str(i)+".wav"))

record_button = Buttons(RECORD_GPIO, '/home/pi/sound_project/dummy.wav')


def wait_button():

    button_queue = queue.Queue()

    for button in buttons:
        button.button.when_pressed = button_queue.put

    queue_event = button_queue.get()
    pressed_gpio = queue_event.pin.number

    handle_button_press(pressed_gpio)


def get_button(gpio):
    for button in buttons:
        if button.gpio == gpio:
            return button
    return INVALID_BUTTON


def handle_button_press(pressed_gpio):
    print("Detected button press on GPIO {0}".format(pressed_gpio))
    pressed_button = get_button(pressed_gpio)
    if pressed_button == INVALID_BUTTON:
        print("Unexpected button press detected")
        return

    if record_button.button.is_pressed:
        pressed_button.record()
    else:
        pressed_button.play_file()


def initialize_usb_device():
    try:
        audio, stream = open_audio()
        close_audio(audio, stream)
    except OSError:
        print("Caught OSError exception, continue...")


if __name__ == '__main__':
    initialize_usb_device()
    while True:
        try:
            wait_button()
        except OSError:
            print("Caught OSError exception, trying again")
