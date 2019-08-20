import logging
import sys
import threading

import plumbum
import psutil
import os

from time import sleep


pyflame = plumbum.local["pyflame"]
flamechartjson = plumbum.local["flame-chart-json"]

FLAMECHARTS_FOLDER = os.getenv('FLAMECHARTS_FOLDER')
CPU_THRESHOLD = int(os.getenv('CPU_THRESHOLD', 90))
CPU_READ_INTERVAL= int(os.getenv('CPU_READ_INTERVAL', 5)
SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', 60))
GUNICORN_PARENT_PID = int(os.getenv('GUNICORN_PARENT_PID', 1))


def setup_logging():
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.level = logging.INFO

    return logger


def get_gunicorn_high_cpu_children_processes(gunicorn_master_pid, threshold=CPU_THRESHOLD):
    gunicorn_subprocesses = psutil.Process(gunicorn_master_pid).children(recursive=True)

    return [children for children in gunicorn_subprocesses if children.cpu_percent(interval=CPU_READ_INTERVAL) > threshold]


def generate_flamechart_files_for_processes(processes):
    for process in processes:
        cpu_profile = "{}/process_{}.profile".format(FLAMECHARTS_FOLDER, process.pid)
        (pyflame(["-s", "5", "-p", process.pid, "--threads", "--flamechart"]) > flamechartjson >
         cpu_profile)()


def start_cpu_monitor_thread(gunicorn_master_pid, sleep_time=SCAN_INTERVAL):
    logger = setup_logging()
    while True:
        gunicorn_high_cpu_children_processes = get_gunicorn_high_cpu_children_processes(gunicorn_master_pid)

        logger.info("Starting Monitoring thread")
        logger.info("{} processes will be profiled.".format(len(gunicorn_high_cpu_children_processes)))

        monitor_thread = threading.Thread(target=generate_flamechart_files_for_processes,
                                          args=(gunicorn_high_cpu_children_processes,))
        monitor_thread.daemon = True
        monitor_thread.start()
        logger.info("Monitoring thread for this cycle is done. Sleeping.\n")

        sleep(sleep_time)


if __name__ == '__main__':
    gunicorn = psutil.Process(GUNICORN_PARENT_PID).children()
    if not gunicorn:
        raise ValueError("Gunicorn processes not found. Check the `GUNICORN_PARENT_PID` env var documentation.")

    start_cpu_monitor_thread(gunicorn[0].pid)
