# Standard Library -----------------------
import time
import datetime
from threading import Thread, Event
from pathlib import Path

# Third Party Library --------------------
import streamlit as st
import pandas as pd
import altair as alt

# Custom Library -------------------------
import sys
sys.path.append("PLUX-API-Python3/M1_312") # Adjust as necessary
import plux
from const import MAC_ADDRESS, SAMPLING_RATE, INTERVAL, DURATION_KEEP_DATA
from logger import logger

# handlerBioPlux.py ----------------------
# >>> Creation of a Custom Class to inherit the SignalsDev callbacks
class SignalsDevice(plux.SignalsDev):
    """Custom class to handle signals from the plux device.

    Inherits from the plux.SignalsDev class and implements methods to
    receive and process data samples collected by the sensors.

    Attributes:
        stop_communication_loop (Event): Event to signal the stopping of the communication loop.
        starttime (datetime): The time when data collection starts.
        filename (int): The filename for saving data, based on the current timestamp.
        data (np.ndarray): Array to store the collected data samples.
    """

    def __init__(self, address: str):
        """Initializes the SignalsDevice with the given address.

        Args:
            address (str): The address of the plux device.
        """
        plux.SignalsDev.__init__(address)
        self.sampling_rate = None # Hz
        self.data = None
        self.sources = None
        self.stop_communication_loop = Event()
        
        # Define the root directory of the repository
        repo_root = Path(__file__).resolve().parent.parent  # Adjust as necessary to reach the root
        # Define the data directory path
        data_dir = repo_root / "data"
        # Create the data directory if it does not exist
        if not data_dir.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
            logger("Data directory created at: {}", data_dir, level='INFO')
        else:
            logger("Data directory already exists at: {}", data_dir, level='INFO')
    
    def onRawFrame(self, nSeq: int, data: tuple):
        """Callback responsible for receiving the data samples collected by the sensors.

        This method is called whenever a new raw frame of data is received.
        It processes the data, logs the start time, and writes the data to a CSV file.

        Args:
            nSeq (int): The sequence number of the received data.
            data (tuple): The data samples collected by the sensors.

        Returns:
            bool: Indicates whether the communication loop should stop.
        """
        # Record Data
        row = [nSeq/self.sampling_rate] + list(data)
        columns = ["nSeq"] + [f"ch{i+1}" for i in range(len(data))]
        new_data = pd.DataFrame([row])  # Convert *data to a pandas DataFrame
        new_data.columns = columns
        if nSeq == 0:
            self.starttime = datetime.datetime.now()
            self.filename = int(self.starttime.timestamp() * 1000)
            self.data = new_data   # Convert data to a pandas DataFrame
        else:
            self.data = pd.concat([self.data, new_data])  # Append new data
        # Remove old data
        if self.data.shape[0] > self.sampling_rate * DURATION_KEEP_DATA:
            self.data = self.data.iloc[-(self.sampling_rate * DURATION_KEEP_DATA):]  # Remove oldest data
        # Write Data to CSV file every second
        if nSeq % self.sampling_rate == 0:
            self.data.iloc[-self.sampling_rate:].to_csv(f"data/{self.filename}.csv", mode='a', header=False, index=False)  # Write the latest self.sampling_rate rows to CSV
        return self.stop_communication_loop.is_set()

    def start_acquisition(self, sampling_rate: int, sources: list):
        """Starts the data acquisition session.

        Args:
            baseFreq (int): The base sampling frequency.
            sources (list): A list of source objects.
        """
        self.sampling_rate = sampling_rate  # Store the sampling rate
        self.sources = sources      # Store the sources
        self.start(self.sampling_rate, self.sources)

    def stop_acquisition(self):
        """Method used to securely stop the real-time data recording.

        This method sets the event to signal the stopping of the data acquisition loop.
        """
        self.stop_communication_loop.set()

def create_source(port, freq_divisor, n_bits, ch_mask):
    source = plux.Source()
    source.port = port
    source.freqDivisor = freq_divisor
    source.nBits = n_bits
    source.chMask = ch_mask
    return source

# main.py ----------------------
class Worker(Thread):
    def __init__(self, mac_address: str, sampling_rate: int, **kwargs):
        super().__init__(**kwargs)
        self.device = None
        self.mac_address = mac_address  # Use the provided MAC address
        self.sampling_rate = sampling_rate  # Use the provided sampling rate
        self.should_stop = Event()
    
    def run(self):
        self.device = SignalsDevice(self.mac_address)
        existSensorsPorts = [port for port, _ in self.device.getSensors().items()]
        sources = [create_source(port, 1, 16, 0x01) for port in existSensorsPorts]
        self.device.start_acquisition(self.sampling_rate, sources)
        self.device.loop()

@st.cache_resource
class ThreadManager:
    worker = None
    
    def get_worker(self):
        return self.worker
    
    def is_running(self):
        return self.worker is not None and self.worker.is_alive()
    
    def start_worker(self, mac_address: str, sampling_rate: int):
        if self.worker is not None:
            self.stop_worker()
        self.worker = Worker(mac_address, sampling_rate, daemon=True)
        self.worker.start()
        return self.worker
    
    def stop_worker(self):
        if self.worker is not None:
            self.worker.device.stop_communication_loop.set()
            self.worker.join()
            self.worker = None

def main():
    thread_manager = ThreadManager()
    
    if thread_manager.is_running():
        worker = thread_manager.get_worker()
        mac_address   = worker.mac_address
        sampling_rate = worker.sampling_rate
    else:
        mac_address   = MAC_ADDRESS
        sampling_rate = SAMPLING_RATE
    
    with st.sidebar:
        # Add a text input for MAC address, disabled if the worker is running
        mac_address = st.text_input("Enter MAC Address", value=mac_address, disabled=thread_manager.is_running())  # Default MAC address
        # Add a number input for sampling rate, disabled if the worker is running
        sampling_rate = st.number_input("Enter Sampling Rate (Hz)", value=sampling_rate, min_value=10, max_value=1000, disabled=thread_manager.is_running())  # Default sampling rate

        if st.button('Start Data Acquisition', disabled=thread_manager.is_running()):
            thread_manager.start_worker(mac_address, sampling_rate)  # Pass the MAC address and sampling rate to the worker
            st.success("Worker has been successfully started.")
            st.rerun()
            
        if st.button('Stop Data Acquisition', disabled=not thread_manager.is_running()):
            thread_manager.stop_worker()
            with st.spinner("Stopping Data Acquisition..."):
                time.sleep(5)
                st.success("Worker has been successfully stopped.")
            st.rerun()

    if not thread_manager.is_running():
        st.markdown('No worker running.')
    else:
        worker = thread_manager.get_worker()
        st.markdown(f'worker: {worker.name}')
    
        with st.spinner("Starting Data Acquisition..."):
            while True:
                if worker and worker.device and worker.device.data is not None:
                    if isinstance(worker.device.data, pd.DataFrame):
                        break  # データが利用可能になったらループを抜ける
                time.sleep(0.5)  # 短い間隔で再確認
        
        # Create text inputs for channel names
        channel_names = []
        num_columns = worker.device.data.shape[1] - 1  # Get the number of data columns
        cols = st.columns(num_columns)  # Create columns for each channel

        for i in range(num_columns):
            with cols[i]:  # Use the corresponding column for each channel
                channel_name = st.text_input(f"Channel {i+1} Name", value=f"Channel {i+1}", key=f"channel_name_{i}")  # Default name
                channel_names.append(channel_name)

        # Dynamically create placeholders for graph drawing
        placeholders = [st.empty() for _ in range(num_columns)]  # Create a list of placeholders

        # If the worker is running, draw the data in real-time on the graph
        while worker.is_alive():
            for i in range(num_columns):
                start_x = worker.device.data['nSeq'].iloc[0]
                end_x = worker.device.data['nSeq'].iloc[0] + DURATION_KEEP_DATA
                chart = alt.Chart(worker.device.data).mark_line().encode(
                    x=alt.X('nSeq', title='Time (sec)', scale=alt.Scale(domain=[start_x, end_x])),  # xlimを指定
                    y=alt.Y(f'ch{i+1}', title=channel_names[i])
                ).properties(
                    width=600,
                    height=250
                )
                placeholders[i].altair_chart(chart)

    # To follow updates in a separate session, rerun periodically
    time.sleep(INTERVAL)
    st.rerun()

if __name__ == '__main__':
    main()