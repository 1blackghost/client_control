import requests
import threading
import time
import os
import subprocess
import sys
import pygetwindow as gw


# Global variables
PING_URL = "https://ytauto.pythonanywhere.com/pingData/1"
CONFIG_URL = "https://ytauto.pythonanywhere.com/getC"

# List to store references to all running threads
running_threads = []

# Flag to signal threads to terminate
terminate_flag = False

def close_all_tor_instances():
    tor_windows = [window for window in gw.getWindowsWithTitle('Tor Browser')]
    for tor_window in tor_windows:
        tor_window.close()

def terminate_function():
    global terminate_flag
    terminate_flag = True

# Function to start an executable
def start_function(executable_path):
    try:
        process = subprocess.Popen([executable_path], shell=True)
        print(f"Started: {executable_path}")
        return process
    except Exception as e:
        print(f"Error starting {executable_path}: {e}")
        return None

# Function to stop an executable
def stop_function(executable_name):
    try:
        close_all_tor_instances()
        subprocess.run(['taskkill', '/F', '/IM', executable_name], check=True)
        print(f"Stopped: {executable_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping {executable_name}: {e}")

# Function to ping a URL
def ping_url(url):
    while not terminate_flag:
        response = requests.get(url)
        print(f"Pinging {url}, Response: {response.text}")
        time.sleep(1)

# Function to download a file
def download_file(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"File downloaded successfully: {filename}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

# Function to fetch and process configuration
def process_config():
    while not terminate_flag:
        config_response = requests.get(CONFIG_URL)
        if config_response.status_code == 200:
            config_data = config_response.json()

            # Check for changes
            if config_data["changes"] == 1:
                # Download getfile1 and getfile2
                download_file(config_data["getfile1"], os.path.basename(config_data["getfile1"]))
                download_file(config_data["getfile2"], os.path.basename(config_data["getfile2"]))

            # Check for start, stop, and terminate
            if config_data["start"] == 1:
                process = start_function("main.exe")
                if process:
                    running_threads.append(process)
            elif config_data["stop"] == 1:
                stop_function("main.exe")
            elif config_data["terminate"] == 1:
                terminate_function()

        time.sleep(1)

# Main function
def main():
    # Create a thread to ping the PING_URL
    ping_thread = threading.Thread(target=ping_url, args=(PING_URL,))
    ping_thread.start()
    running_threads.append(ping_thread)

    # Create a thread to fetch and process configuration
    config_thread = threading.Thread(target=process_config)
    config_thread.start()
    running_threads.append(config_thread)

    # Wait for the terminate flag to be set
    for thread in running_threads:
        thread.join()

if __name__ == "__main__":
    main()
