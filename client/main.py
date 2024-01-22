import requests
import threading
import time
import os
import subprocess
import sys
import pygetwindow as gw
from datetime import datetime

# Global variables
PING_URL = "https://ytauto.pythonanywhere.com/pingData/1"
CONFIG_URL = "https://ytauto.pythonanywhere.com/getC"

# Global variable to store configuration data
config_data = {}

# List to store references to all running threads
running_threads = []

# Flag to signal threads to terminate
terminate_flag = False

def close_all_tor_instances():
    requests.get("https://ytauto.pythonanywhere.com/logged/[-]Closing All Tor Instances..")

    tor_windows = [window for window in gw.getWindowsWithTitle('Tor Browser')]
    for tor_window in tor_windows:
        tor_window.close()

def terminate_function():
    global terminate_flag
    terminate_flag = True

# Function to start an executable
def start_function(executable_path):
    global current_datetime
    current_datetime = datetime.now()

    # Format the current date and time in 12-hour format
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %I:%M:%S %p")

    try:
        process = subprocess.Popen([executable_path], shell=True)
        print(f"Started: {executable_path}")
        return process
    except Exception as e:
        print(f"Error starting {executable_path}: {e}")
        return None

# Function to stop an executable
def stop_function(executable_name):
    global end_time
    global current_datetime
    end_time = datetime.now()

    # Calculate the runtime
    runtime = end_time - current_datetime
    current_datetime=end_time
    hours, remainder = divmod(runtime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_runtime = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
    requests.get("https://ytauto.pythonanywhere.com/logged/[+]Total Runtime: "+str(formatted_runtime))






    try:
        subprocess.run(['taskkill', '/F', '/IM', executable_name], check=True)
        print(f"Stopped: {executable_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error stopping {executable_name}: {e}")
        return 1

# Function to ping a URL and get configuration data
def ping_data(url):
    global config_data
    while not terminate_flag:
        response = requests.get(url)
        if response.status_code == 200:
            config_data = response.json()
            print("Received Config Data:", config_data)
        else:
            print(f"Failed to get configuration data. Status code: {response.status_code}")
        time.sleep(2)

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
        global config_data
        c = datetime.now()

        # Format the current date and time in 12-hour format with date
        get = c.strftime("%Y-%m-%d %I:%M:%S %p")

        # Check for changes
        if config_data.get("changes") == 1:
            requests.get("https://ytauto.pythonanywhere.com/logged/Upload Event=> @"+str(get))
            requests.get("https://ytauto.pythonanywhere.com/logged/[+]Detected Changes in config or main.exe")
            requests.get("https://ytauto.pythonanywhere.com/logged/[+]Calling Halt Programs for updation..")

            close_all_tor_instances()
            if stop_function("main.exe") != 1:
                requests.get("https://ytauto.pythonanywhere.com/logged/[+]Success! Killed main.exe!")
            else:
                requests.get("https://ytauto.pythonanywhere.com/logged/[-]Main.exe was not found to kill.maybe you didnt start?")
            requests.get("https://ytauto.pythonanywhere.com/logged/[+]Downloading updated configurations.Please wait..for confirmation!")

            # Download getfile1 and getfile2
            download_file(config_data.get("getfile1", ""), os.path.basename(config_data.get("getfile1", "")))
            requests.get("https://ytauto.pythonanywhere.com/logged/[+]Main.exe Updated In Client Side")

            download_file(config_data.get("getfile2", ""), os.path.basename(config_data.get("getfile2", "")))
            requests.get("https://ytauto.pythonanywhere.com/logged/[+]Settings Updated In Client Side")


        # Check for start, stop, and terminate
        if config_data.get("terminate") == 1:
            requests.get("https://ytauto.pythonanywhere.com/logged/Restart Event=> @"+str(get))
            close_all_tor_instances()
            requests.get("https://ytauto.pythonanywhere.com/logged/[+]Restarting All.Intialising Sequence..")
            # Stop the main process
            # Terminate the script
            if stop_function("main.exe") != 1:
                requests.get("https://ytauto.pythonanywhere.com/logged/[+]Success! Killed main.exe!")
            else:
                requests.get("https://ytauto.pythonanywhere.com/logged/[-]Main.exe was not found to kill.maybe you didnt start?")
            start_function("main.exe")
            requests.get("https://ytauto.pythonanywhere.com/logged/[+]Success! main.exe was started")

        elif config_data.get("start") == 1:
            requests.get("https://ytauto.pythonanywhere.com/logged/Start Event=> @"+str(get))
            requests.get("https://ytauto.pythonanywhere.com/logged/[+]Starting main.exe")
            # Start the main process
            process = start_function("main.exe")
            if process:
                running_threads.append(process)
            requests.get("https://ytauto.pythonanywhere.com/logged/[+]Success started main.exe")


        elif config_data.get("stop") == 1:
            requests.get("https://ytauto.pythonanywhere.com/logged/Stop Event=> @"+str(get))
            close_all_tor_instances()
            requests.get("https://ytauto.pythonanywhere.com/logged/[-]Stopping main.exe")
            if stop_function("main.exe") != 1:
                requests.get("https://ytauto.pythonanywhere.com/logged/[+]Success! Killed main.exe!")
            else:
                requests.get("https://ytauto.pythonanywhere.com/logged/[-]Main.exe was not found to kill.maybe you didnt start?")

        time.sleep(1)

# Main function
def main():
    global config_data
    while not terminate_flag:
        # Create a thread to ping the PING_URL and get configuration data
        ping_thread = threading.Thread(target=ping_data, args=(PING_URL,))
        ping_thread.start()
        running_threads.append(ping_thread)

        # Create a thread to fetch and process configuration
        config_thread = threading.Thread(target=process_config)
        config_thread.start()
        running_threads.append(config_thread)

        # Wait for the terminate flag to be set
        for thread in running_threads:
            thread.join()

        # Clear the running threads list
        running_threads.clear()

        # If terminate_flag is set, restart the script
        if terminate_flag:
            print("Restarting the script...")
            time.sleep(5)  # Add a delay before restarting to avoid rapid restarts
            os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    main()
