# Installation

```
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To generate a set of simulated sensor data (takes 35 seconds):

```
python main.py
```

To view this in a browser:

```
python srec/server.py
```

All the simulated data is a sine wave, so you should see a sine wave for every sensor in the graph.


# Overview

The task set included the following spec requirements:

* Extensible to work with many devices

This is hard to simulate (as the device reading code is likely to be different). However, the sensors can be defined simply in `config.yaml` and they will have their own entry in the database after running. A subclass of DataReader would be required to handle - for instance - reading from serial bus / usb or whatever the source was.

* Failure tolerant (no internet, device malfunction)

There's no Internet usage here. It's hard to simulate a device malfunction because that would be in the reader code. All that would be required is to stop the thread running that code. If that was to happen, the thread that captures the data would just see an empty buffer, and therefore write nothing to the database.

* Be capable of serving a basic local diagnostics UI, showing latest value for all captured data attributes

The UI is a seperate program. It just shows the last block of data for one sensor.


Comments
--------

Although this program is not doing a lot as such, it still has some complexity. We have 3 different programming languages, a database, a web server and a webpage with AJAX callbacks. I've tried to show that I can cover all of those elements, and yet we are still missing multi-channel sensors, sensors with text data, internet uploading and so much more. I've include a minimal set of unit tests more so that you can see I know how to add tests (I mean, I could also start to mock the DB for tests but this really starts to add a lot of work).

This code was tested with Python 3.11 on a Linux Mint 21 64-bit system.
