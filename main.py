import sys
import math
import time
import yaml
import threading

from src.database import create_database, write_binary_data, create_ingestion_point, get_last_data

CONFIG_FILE = 'setup.yaml'
# max size of single buffer
BUFFER_SIZE = 2000
# how long to read data for, in seconds
READ_TIME = 30


class DataWriter:
    def __init__(self, name, frequency):
        self.name = name
        self.frequency = frequency
        self.buffer = []
        self.thread = threading.Thread(target=self.write_data)
        self.running = False
        self.buffer_lock = threading.Lock()

    def write_data(self):
        # writes data
        sleep_time = 1.0 / self.frequency
        # just add a simple sine wave for now
        sin_delta = (math.pi * 2.0) / self.frequency
        angle = 0.0
        while self.running is True:
            with self.buffer_lock:
                self.buffer.append(math.sin(angle))
                angle += sin_delta
            # not totally accurate as we lose time appending, but it's just a simulation
            time.sleep(sleep_time)

    def start(self):
        self.running = True
        self.buffer = []
        self.thread.start()

    def stop(self):
        self.running = False

    def __repr__(self):
        return f'{self.name}, {self.frequency}Hz'


class DataHandler:
    def __init__(self, writer, read_time):
        self.writer = writer
        self.read_time = read_time
        self.thread = None
        self.running = False

    def read_data(self):
        # create the database main object, and put in the start time
        table_id = create_ingestion_point(self, self.writer.name, self.writer.frequency)
        # calculate how long to check the data
        wait_time = (1.0 / self.writer.frequency) * BUFFER_SIZE
        self.thread = threading.Thread(target=self.reader_thread,
                                       args=(table_id, wait_time, self.read_time, self.writer))
        self.thread.start()
        self.running = True

    def reader_thread(self, table_id, wait_time, read_time, writer):
        start_time = time.time()
        writer.start()
        while (time.time() - start_time) < read_time:
            with writer.buffer_lock:
                if len(writer.buffer) > BUFFER_SIZE:
                    buffer_data = writer.buffer[:BUFFER_SIZE]
                    del writer.buffer[:BUFFER_SIZE]
                    if write_binary_data(table_id, buffer_data) is False:
                        print('Error: Could not write data')
                        writer.stop()
                        return
            time.sleep(wait_time)
        # write final buffer entry
        with writer.buffer_lock:
            write_binary_data(table_id, writer.buffer[:BUFFER_SIZE])
        writer.stop()
        print(f'* Finished {writer.name}')
        self.running = False


def get_sensors():
    with open(CONFIG_FILE) as stream:
        try:
            config_data = yaml.safe_load(stream)
            data_sources = []
            for i in config_data['sensors']:
                data_sources.append(DataWriter(i['name'], i['frequency']))
            return data_sources
        except yaml.YAMLError as ex:
            print(f'Error: Could not read config file {CONFIG_FILE}: {ex}')
            sys.exit(False)
        except KeyError:
            print(f'Error: Config file missing values')
            sys.exit(False)


if __name__ == '__main__':
    print('* Creating database')
    create_database()
    sensors = get_sensors()
    print(f'* Got {len(sensors)} sensors from {CONFIG_FILE}')
    readers = [DataHandler(x, READ_TIME) for x in sensors]
    for i in readers:
        i.read_data()
    print(f'* Starting data reads ({READ_TIME} seconds)')
    # wait for all threads to finish
    total_wait = 0
    while all([x.running for x in readers]):
        time.sleep(5)
        total_wait += 5
        print(f'  Waiting.. ({total_wait} seconds total)')
    print('* Finished')
