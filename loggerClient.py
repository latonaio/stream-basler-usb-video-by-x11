#!/usr/bin/python3

import asyncio
import os
import queue
import sys
import traceback
from re import match
from time import time

class LoggerQueue():
    def __init__(self):
        self.queue = queue.Queue()
        self.close = False

    def stop(self):
        self.close = True
        self.queue.put(None)

    def generator(self):
        while not self.close:
            try:
                res = self.queue.get(timeout=0.1)
                if res is None:
                    return
                yield res
            except queue.Empty:
                pass

    def set_log_message(self, dic):
        self.queue.put(dic)


class LoggerClient():
    logger_queue = None

    def __init__(self, component, *, file_log_level=4, stdout_log_level=4):
        self.component = component
        self.pid = os.getpid()
        self.logger_queue = LoggerQueue()
        self.queue_generator = self.logger_queue.generator()
        self.file_log_level = file_log_level
        self.stdout_log_level = stdout_log_level


    def print(self, message, level=4, output_type=1):
        dic = {
            'component': self.component,
            'level': level,
            'message': str(message),
            'pid': self.pid
        }
        if self.file_log_level >= level:
            self.logger_queue.set_log_message(dic)
        if output_type == 1 and self.stdout_log_level >= level:
            print(",".join([self.component, str(self.pid), message]))

    def function_log(self, func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                func_name = func.__name__
                st = time()
                # start log
                self.print("Start: " + func_name, 4)
                try:
                    res = await func(*args, **kwargs)
                except Exception as e:
                    self.print(str(e), 1)
                    self.print(traceback.format_exc(), 1)
                    raise
                # finish log
                message = \
                    "Finish:" + func_name + "(time:{})".format(time()-st)
                self.print(message, 4)
                return res
            return async_wrapper
        else:
            def wrapper(*args, **kwargs):
                func_name = func.__name__
                st = time()
                # start log
                self.print("Start: " + func_name, 4)
                try:
                    res = func(*args, **kwargs)
                except Exception as e:
                    self.print(str(e), 1)
                    self.print(traceback.format_exc(), 1)
                    raise
                # finish log
                message = \
                    "Finish:" + func_name + "(time:{})".format(time()-st)
                self.print(message, 4)
                return res
            return wrapper
