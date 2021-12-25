import wave
from gpiozero import Button
import pyaudio
import subprocess
import os
import sys

form_1 = pyaudio.paInt16  # 16-bit resolution
chans = 1  # 1 channel
samp_rate = 48000  # default value for the fifine mic
chunk = 4096  # 2^12 samples for buffer
record_secs = 5  # seconds to record
dev_index = 1  # device index found by p.get_device_info_by_index(ii)
wav_output_filename = '/home/pi/sound_project/test1.wav'  # name of .wav file

button = Button(2)


def record():
    audio = pyaudio.PyAudio()  # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format=form_1, rate=samp_rate, channels=chans, \
                        input_device_index=dev_index, input=True, \
                        frames_per_buffer=chunk)
    print("recording")
    frames = []

    # loop through stream and append audio chunks to frame array
    # for ii in range(0, int((samp_rate / chunk) * record_secs)):
    while button.is_pressed:
        data = stream.read(chunk)
        frames.append(data)

    print("finished recording")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()
    save_file(audio, frames)


def save_file(audio, frames):
    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename, 'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()


def play_file():
    print("Replaying")
    os.system("omxplayer -o local " + wav_output_filename)
    print("Done")


if __name__ == '__main__':
    while True:
        button.wait_for_press()
        record()
        button.wait_for_press()
        play_file()
