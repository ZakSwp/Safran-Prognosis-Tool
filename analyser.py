import numpy as np
from PyQt5.QtCore import QThread 
from config import *
from acquisition import *


class Analyser(QThread):
    def __init__(self, QMainWindow):
        self.main_window = QMainWindow
        self.spectrum_config = {SPECTRE1: [False,QMainWindow.Sp1GraphicsView], SPECTRE2: [False,QMainWindow.Sp2GraphicsView]}
        self.plotManager = self.main_window.plotManager
        self.acqThread=self.main_window.acqThread
        self.sample_rate =self.acqThread.sample_rate


    def enable_spectrum(self, spectrum_list):
        """
        :param spectrum_list: List of names of spectrums to be activated
        """
        for s in spectrum_list:
            while len(self.plotManager.plot_data[s])<self.plotManager.window_length:
                self.sample_rate=self.acqThread.sample_rate
                print("Acquired datapoints less than window size. Skipping {} ms to acquire more.".format(self.sample_rate))
                self.msleep(self.sample_rate)
                continue
            self.spectrum_config[s][0]=True

    def disable_spectrum(self,spectrum_list):
        pass
def compute_fft(self, signal_name, window_length=200):
    """
    Compute FFT on specified signal with Hanning window
    
    Args:
        signal_name: Key from plot_data dict (SIGNAL1, SIGNAL2, etc.)
        window_length: Number of samples for FFT window
    
    Returns:
        freqs: Frequency bins (Hz)
        magnitude: Magnitude spectrum
    """
    if signal_name not in self.plot_data:
        print(f"Error: {signal_name} not found in plot data")
        return None, None
    
    signal_buffer = np.array(self.plot_data[signal_name])    
    if len(signal_buffer) < window_length:
        return None, None  # Insufficient samples
    
    signal_window = signal_buffer[-window_length:]
    
    windowed = signal_window * np.hanning(window_length) # Apply Hanning window
    
    #(real signal, so use rfft)
    fft_result = np.fft.rfft(windowed)
    magnitude = np.abs(fft_result)
    
    # Frequency bins (0 to Nyquist)
    freqs = np.fft.rfftfreq(window_length, d=1/self.sample_rate)
    
    return freqs, magnitude