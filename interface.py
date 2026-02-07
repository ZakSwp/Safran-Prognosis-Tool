from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer, QDateTime
import pyqtgraph as pg 
import numpy as np
from collections import deque
from config import *
from acquisition import *


class MainUI(QMainWindow):

    def __init__(self):
        super(MainUI, self).__init__()
        loadUi("main.ui", self)
        self.visualizationPanel = self.VisualizationPanel
        self.sidePanel = self.SidePanel
        self.timeLabel = self.Gear1UptimeOut
        self.start_time = QDateTime.currentDateTime()
        if self.timeLabel:
            self.timer = QTimer()
            self.timer.timeout.connect(self.updateTime)
            self.timer.start(10)  # 1 ms
            self.updateTime()
        else:
            print("Failed to locate label")
        #self.analyser = Analyser(self)
        self.plotManager = PlotManager(self)
        self.acqThread = DataAcquisitionThread(self)
        self.acqThread.new_data.connect(self.plotManager.update_plots_array)
        self.StartPushButton.clicked.connect(self.toggle_acquisition) 

    def toggle_acquisition(self):
        if not self.acqThread.running:
            self.acqThread.start_acquisition()
            self.StartPushButton.setText("Stop Acqusition")
        else:
            self.acqThread.stop_acquisition()
            self.StartPushButton.setText("Start Acqusition")
    
    def set_sample_rate(self,sr):
        self.analyser.sample_rate = sr
        self.acqThread.sample_rate = sr

    def set_window_length(self,wl):
        self.plotManager.window_length = wl

    def updateTime(self):
        timelabels = [self.Gear1UptimeOut, self.Gear2UptimeOut]
        current_time = QDateTime.currentDateTime()
        elapsed_ms = self.start_time.msecsTo(current_time)
        hours = elapsed_ms // 3600000
        minutes = (elapsed_ms % 3600000) // 60000
        seconds = (elapsed_ms % 60000) // 1000
        milliseconds = elapsed_ms % 1000
        
        # Format with leading zeros
        current_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        for label in timelabels:
            label.setText(current_time_str)


class PlotManager():
    def __init__(self, QMainWindow,bgColor= (185, 185, 185), axColor= (40,40,40),max_points=1000):
        self.mainwindow = QMainWindow
        

        plotList = [plot for frame in (self.mainwindow.RTSignalVizFrame, self.mainwindow.SpectreVizFrame) for plot in frame.children() if isinstance(plot, pg.PlotWidget)]
        self.plotNameList = {}
        for p in plotList:
            self.plotNameList[p.objectName()]=p
        self.bgColor = '#1a1a1a' #bgColor
        self.axColor = '#606060' #(0,125,2) #axColor

        self.window_length = 500
        self.plot_data = {} #Dict of plotnames: value deque
        self.plot_curves = {} #Dict of plotnames: curve object
        self.time_data = deque(maxlen=self.window_length)

        self._init_plots()

    def _init_plots(self):
        for plot in self.plotNameList.values():
            try:
                plot.setBackground(self.bgColor)
                plot.setLimits(xMin = 0)
                plot.showGrid(x=True, y=True)
                plot.setMouseEnabled(x=False, y=True) 
                for axis in ('left', 'bottom'):
                    ax = plot.getAxis(axis)
                    ax.setPen(self.axColor)
                    ax.setTextPen(self.axColor)
                plot.setLabel('left', 'Amplitude', units='V')
                plot.setLabel('bottom', 'Time', units='s')   
                self.plot_data[plot.objectName()] = deque(maxlen=self.window_length)# Create a data buffer for this plot
                self.plot_curves[plot.objectName()] = plot.plot( pen=pg.mkPen(color="#04f300", width=2),  
                                                                #symbol='o',symbolSize=3,symbolBrush="#fffb00",symbolPen=None,
                                                                name='Signal')# Create a curve object for this plot
            except Exception as e:
                print("Error initializing plot {}: {}".format(plot, e))
            
            self.plotNameList[SPECTRE2].setLabel('left', 'Magnitude')
            self.plotNameList[SPECTRE2].setLabel('bottom', 'Frequency', units='Hz')
            self.plot_curves[SPECTRE2] = self.plotNameList[SPECTRE2].plot(pen=pg.mkPen(color="#f30000", width=2),  
                                                                name='Spectrum')
            self.plotNameList[SPECTRE1].setLabel('left', 'Magnitude')
            self.plotNameList[SPECTRE1].setLabel('bottom', 'Frequency', units='Hz')
            self.plot_curves[SPECTRE1] = self.plotNameList[SPECTRE1].plot(pen=pg.mkPen(color="#f30000", width=2),  
                                                                name='Spectrum')


    def _update_signal(self, plot_name, value):
        plot = self.plotNameList[plot_name]
        self.plot_data[plot_name].append(value)
        # deques to numpy arrays for plotting
        x_data = np.array(self.time_data)
        plot.setLimits(xMin = min(x_data)) #update rendering minimum x boundary
        y_data = np.array(self.plot_data[plot_name])
        self.plot_curves[plot_name].setData(x_data, y_data)
    
    def _update_signal_array(self, plot_name, values):
        plot = self.plotNameList[plot_name]
        self.plot_data[plot_name].extend(values)
        x_data = np.array(self.time_data)# deques to numpy arrays for plotting
        plot.setLimits(xMin = min(x_data)) #update rendering minimum x boundary
        y_data = np.array(self.plot_data[plot_name])
        self.plot_curves[plot_name].setData(x_data, y_data)
    
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
        
        # Get signal buffer
        signal_buffer = np.array(self.plot_data[signal_name])
        
        # Check if enough samples
        if len(signal_buffer) < window_length:
            return None, None  # Not enough data yet
        
        # Extract last window_length samples
        signal_window = signal_buffer[-window_length:]
        
        # Apply Hanning window
        windowed = signal_window * np.hanning(window_length)
        
        # Compute FFT (real signal, so use rfft)
        fft_result = np.fft.rfft(windowed)
        magnitude = np.abs(fft_result)
        
        # Frequency bins (0 to Nyquist)
        freqs = np.fft.rfftfreq(window_length, d=1/100)
        
        return freqs, magnitude

    def update_plots(self, new_data_dict):
        """
        Update plots with new data.
        new_data_dict: Dictionary of the shape:\n
        {'timestamp': str,
        signal1_name: float,
        signal2_name: float,
        signal3_name: float,
        signal4_name : float}
        """
        # Time update
        timestamp = new_data_dict.pop('timestamp')  # Extract and remove from dict
        self.time_data.append(timestamp)
        # Update each plot with new data
        for plot_name, new_value in new_data_dict.items():
            if plot_name in self.plot_data.keys():
                self._update_signal(plot_name, new_value)
            else:
                print(f"Warning: Unknown plot {plot_name}")
    
    def update_plots_array(self, new_data_array):
        timestamps = new_data_array.pop('timestamp')  # Extract and remove from dict
        self.time_data.extend(timestamps)
        for plot_name, new_values in new_data_array.items():
            if plot_name in self.plot_data.keys():
                self._update_signal_array(plot_name, new_values)
            else:
                print(f"Warning: Unknown plot {plot_name}")
                
        freqs, magnitude = self.compute_fft(SIGNAL2, window_length=200)
        if freqs is not None:
            # Assuming you have an FFT curve already created in initPlots
            self.plot_curves[SPECTRE2].setData(freqs, magnitude)
        freqs1, magnitude1 = self.compute_fft(SIGNAL1, window_length=200)
        if freqs1 is not None:
            # Assuming you have an FFT curve already created in initPlots
            self.plot_curves[SPECTRE1].setData(freqs1, magnitude1)




        




