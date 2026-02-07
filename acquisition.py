from PyQt5.QtCore import pyqtSignal, QThread
import time
import numpy as np
from config import *
import pandas as pd

class DataAcquisitionThread(QThread):
    """Thread that acquires/simulates data"""
    new_data = pyqtSignal(dict)  # Signal with new data points
    
    def __init__(self, mainWindow , sample_rate=1000, emit_rate = 20):
        super().__init__()
        self.mainWindow = mainWindow
        self.emit_rate = emit_rate
        self.sample_rate = sample_rate  # Hz
        self.batch_size = sample_rate//emit_rate
        self.running = False
    
    def start_acquisition(self):
        self.running = True
        self.start()

#    def run_obsolete(self):
#        sample_interval = 1000 / self.sample_rate  # ms
#        emit_interval = 1000/self.emit_rate
#        while self.running:
#            batch_data = {
#                'timestamp': [],
#                SIGNAL1: [],
#                SIGNAL2: [],
#                SPECTRE1: [],
#                SPECTRE2: [],
#            }
#            for _ in range(self.batch_size):
#            # Simulate or acquire real data
#                timestamp = time.time()
#                batch_data['timestamp'].append(timestamp)
#                batch_data[SIGNAL1].append(25 + np.random.randn() * 2)
#                batch_data[SIGNAL2].append(np.sin(5*timestamp))
#                batch_data[SPECTRE1].append(1500 + np.random.randn() * 100)
#                batch_data[SPECTRE2].append(12 + np.random.randn() * 0.5)
#
#                self.msleep(int(sample_interval)) #simulate sampling speed
#            self.msleep(int(emit_interval))     
#            self.new_data.emit(batch_data) #emit emit_rate times per second
#            self.buffer = []
#            #Emit signal containing new data points, wait the period length then, if running == True still holds, repeat


    def run_normal(self):
        sample_interval = 1000 / self.sample_rate  # ms
        emit_interval = 1000/self.emit_rate
        t_start = time.time()
        sample_count = 0
        
        while self.running:
            # Generate batch_size samples at once
            t_current = time.time()
            t_elapsed = t_current - t_start
            
            # Time array for this batch
            t_batch = t_elapsed + np.arange(self.batch_size) / self.sample_rate
            
            batch_data = {
                'timestamp': t_batch,
                SIGNAL1: 25 + np.random.randn(self.batch_size) * 2,
                SIGNAL2: np.sin(5 * t_batch),
                SPECTRE1: 1500 + np.random.randn(self.batch_size) * 100,
                SPECTRE2: 12 + np.random.randn(self.batch_size) * 0.5,
            } #use a self.buffer instead of batch_data if memory proves to be an issue
            
            self.new_data.emit(batch_data)#emit emit_rate times per second
            sample_count += self.batch_size
            
            # Sleep until next emission time
            self.msleep(int(emit_interval))
            #Emit signal containing new data points, wait the period length then, if running == True still holds, repeat
    
    def run(self,csv_path="data\accel_physics_aug.csv"):
        try:
            df = pd.read_csv(csv_path)# Load entire CSV once
            
            # Validate columns
            required_cols = ['Time_s','Ax_ms2','Ay_ms2','Az_ms2']
            if not all(col in df.columns for col in required_cols):
                print(f"Error: CSV missing required columns. Found: {df.columns.tolist()}")
                return
            
            total_samples = len(df)
            emit_interval = 1000 / self.emit_rate  # ms
            
            idx = 0
            while self.running and idx < total_samples:
                # Extract batch
                batch_size = 5
                end_idx = min(idx + batch_size, total_samples)
                batch = df.iloc[idx:end_idx]
                
                batch_data = {
                    'timestamp': batch['Time_s'].values,
                    SIGNAL1: batch['Ax_ms2'].values,
                    SIGNAL2: batch['Ay_ms2'].values,
                }
                
                self.new_data.emit(batch_data)
                idx = end_idx
                self.msleep(int(emit_interval))
            
            
            self.stop_acquisition()# Signal completion
        except FileNotFoundError:
            print(f"Error: CSV file not found: {csv_path}")
        except Exception as e:
            print(f"Error reading CSV: {e}")


    def stop_acquisition(self):
        self.running = False
        self.wait()