import pyaudio
import time
import numpy as np
from matplotlib import pyplot as plt
import scipy.signal as signal



CHANNELS = 2
RATE = 44100

p = pyaudio.PyAudio()
fulldata = np.array([])
dry_data = np.array([])

def main():
    stream = p.open(format=pyaudio.paFloat32,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    input=True,
                    stream_callback=callback)

    stream.start_stream()

    while stream.is_active():
        time.sleep(10)
        stream.stop_stream()
    stream.close()

    numpydata = np.hstack(fulldata)
    plt.plot(numpydata)
    plt.title("Wet")
    plt.show()

def callback():
    print(1)