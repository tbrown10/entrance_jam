import subprocess
from time import sleep
from threading import Thread
import sys
from twython import Twython
import datetime

CONSUMER_KEY = 'lLV8SYpYyEQz4j2uutuFSDU5p'
CONSUMER_SECRET = '4hIETlpVouvKbNoAI6N0Zjdxup36iX0qHAwv6TpwkvQAokUwyI'
ACCESS_KEY = '931768982683525120-JZO3xfCad99KlI4Drwytqsy9pW6C9wu'
ACCESS_SECRET = 'OWANDCwH9XGrzi5Ini870oGx4pyhzWOZDfpmbb0DobKFN'

api = Twython(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_KEY,ACCESS_SECRET)

# Edit these for how many people/devices you want to track
occupant = ["Taylor","Adam","Sam","Thomas","Landon"]

# MAC addresses for our phones
address = ["1c:91:48:b0:63:1f","7c:fa:df:9a:51:b0","8c:29:37:12:65:de","b4:4b:d2:f4:0e:11","2c:33:61:85:51:03"]

# Sleep once right when this script is called to give the Pi enough time
# to connect to the network
# disabled for testing
# sleep(60)

# Some arrays to help minimize streaming and account for devices
# disappearing from the network when asleep
firstRun = [1] * len(occupant)
presentSent = [0] * len(occupant)
notPresentSent = [0] * len(occupant)
counter = [0] * len(occupant)

# Function that checks for device presence
def whosHere(i):

    # 30 second pause to allow main thread to finish arp-scan and populate output
    sleep(30)

    # Loop through checking for devices and counting if they're not present
    while True:

        # Exits thread if Keyboard Interrupt occurs
        if stop == True:
            print("Exiting Thread")
            exit()
        else:
            pass

        # If a listed device address is present print and stream
        if address[i] in output:
            print(occupant[i] + "'s device is connected to your network")
            if presentSent[i] == 0:
                print(occupant[i] + " present streamed")
                now = datetime.datetime.now()
                date_string = now.strftime('%Y-%m-%d-%H-%M-%S')
                api.update_status(status=occupant[i] + ' is home. ' + date_string)
		# Reset counters so another stream isn't sent if the device
                # is still present
                firstRun[i] = 0
                presentSent[i] = 1
                notPresentSent[i] = 0
                counter[i] = 0
                sleep(900)
            else:
                # If a stream's already been sent, just wait for 15 minutes
                counter[i] = 0
                sleep(900)
        # If a listed device address is not present, print and stream
        else:
            print(occupant[i] + "'s device is not present")
            # Only consider a device offline if it's counter has reached 30
            # This is the same as 15 minutes passing
            if counter[i] == 30 or firstRun[i] == 1:
                firstRun[i] = 0
                if notPresentSent[i] == 0:
                    print(occupant[i] + " not present streamed")
                    now = datetime.datetime.now()
                    date_string = now.strftime('%Y-%m-%d-%H-%M-%S')
                    api.update_status(status=occupant[i] + ' left. ' + date_string)
                    # Reset counters so another stream isn't sent if the device
                    # is still present
                    notPresentSent[i] = 1
                    presentSent[i] = 0
                    counter[i] = 0
                else:
                    # If a stream's already been sent, wait 30 seconds
                    counter[i] = 0
                    sleep(30)
            # Count how many 30 second intervals have happened since the device 
            # disappeared from the network
            else:
                counter[i] = counter[i] + 1
                print(occupant[i] + "'s counter at " + str(counter[i]))
                sleep(30)


# Main thread

try:

    # Initialize a variable to trigger threads to exit when True
    global stop
    stop = False

    # Start the thread(s)
    # It will start as many threads as there are values in the occupant array
    for i in range(len(occupant)):
        t = Thread(target=whosHere, args=(i,))
        t.start()

    while True:
        # Make output global so the threads can see it
        global output
        # Assign list of devices on the network to "output"
        output = subprocess.check_output("sudo arp-scan -l", shell=True)
        # Wait 30 seconds between scans
        sleep(30)

except KeyboardInterrupt:
    # On a keyboard interrupt signal threads to exit
    stop = True
    exit()
