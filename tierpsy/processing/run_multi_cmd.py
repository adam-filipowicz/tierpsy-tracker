# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 23:43:30 2015

@author: ajaver
"""

#import os

import sys
import os
import time
import subprocess as sp
from functools import partial
from io import StringIO
from tierpsy.helper.misc import TimeCounter, ReadEnqueue

GUI_CLEAR_SIGNAL = '+++++++++++++++++++++++++++++++++++++++++++++++++'

class CapturingOutput(list):
    '''modified from http://stackoverflow.com/questions/1218933/can-i-redirect-the-stdout-in-python-into-some-sort-of-string-buffer'''

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend([x + '\n' for x in self._stringio.getvalue().splitlines()])
        sys.stdout = self._stdout

ON_POSIX = 'posix' in sys.builtin_module_names



class StartProcess():

    def __init__(self, cmd, local_obj='', is_debug = True):
        self.is_debug = is_debug
        self.output = ['Started\n']

        if local_obj:
            with CapturingOutput() as output:
                if cmd[0] == sys.executable:
                    cmd = cmd[1:]
                self.obj_cmd = local_obj(cmd)

                self.cmd = self.obj_cmd.start()



            self.output += output

        else:
            self.obj_cmd = ''
            self.cmd = cmd
            self.output = ['Started\n']

        self.output += [cmdlist2str(self.cmd) + '\n']

        self.proc = sp.Popen(self.cmd, stdout=sp.PIPE, stderr=sp.PIPE,
                             bufsize=1, close_fds=ON_POSIX,
                             env=dict(os.environ.copy(),OMP_NUM_THREADS='1'))
        self.buf_reader = ReadEnqueue(self.proc.stdout)

    def read_buff(self):
        while True:
            # read line without blocking
            line = self.buf_reader.read()
            if line is not None:
                self.output.append(line)
            else:
                break
        # store only the last line
        self.output = self.output[-1:]

    def close(self):
        if self.proc.poll() != 0:
            error_outputs = self.proc.stderr.read().decode("utf-8")
            # print errors details if there was any
            self.output[-1] += 'ERROR: \n'

            #I want to add only the last line of the error. No traceback info in order to do not overwhelm the user.
            dd = error_outputs.split('\n')
            if len(dd) > 1:
                self.output[-1] += dd[-2] + '\n'

            if self.is_debug:
                self.output[-1] += error_outputs
                self.output[-1] += cmdlist2str(self.cmd) + '\n'
                self.proc.stderr.flush()

        if self.obj_cmd and self.proc.poll() == 0:
            with CapturingOutput() as output:
                self.obj_cmd.clean()
            self.output += output

        self.proc.wait()
        self.proc.stdout.close()
        self.proc.stderr.close()


def RunMultiCMD(cmd_list,
                local_obj='',
                max_num_process=3,
                refresh_time=10,
                is_debug = True):
    '''Start different process using the command is cmd_list'''


    start_obj = partial(StartProcess, local_obj=local_obj, is_debug=is_debug)

    total_timer = TimeCounter() #timer to meassure the total time

    cmd_list = cmd_list[::-1]  # since I am using pop to get the next element i need to invert the list to get athe same order
    tot_tasks = len(cmd_list)
    if tot_tasks < max_num_process:
        max_num_process = tot_tasks

    # initialize the first max_number_process in the list
    finished_tasks = []

    current_tasks = []
    for ii in range(max_num_process):
        cmd = cmd_list.pop()
        current_tasks.append(start_obj(cmd))

    # keep loop tasks as long as there are tasks in the list
    while current_tasks:
        time.sleep(refresh_time)

        print(GUI_CLEAR_SIGNAL)
        os.system(['clear', 'cls'][os.name == 'nt'])

        # print info of the finished tasks
        for task_finish_msg in finished_tasks:
            sys.stdout.write(task_finish_msg)

        # loop along the process list to update output and see if there is any
        # task finished
        next_tasks = []

        #I want to close the tasks after starting the next the tasks. It has de disadvantage of
        #requiring more disk space, (required files for the new task + the finished files)
        #but at least it should start a new tasks while it is copying the old results.
        tasks_to_close = []

        for task in current_tasks:
            task.read_buff()
            if task.proc.poll() is None:
                # add task to the new list if it hasn't complete
                next_tasks.append(task)
                sys.stdout.write(task.output[-1])
            else:
                # close the task and add its las output to the finished_tasks
                # list
                tasks_to_close.append(task)
                # add new task once the previous one was finished
                if cmd_list and len(next_tasks) < max_num_process:
                    cmd = cmd_list.pop()
                    next_tasks.append(start_obj(cmd))

        # if there is stlll space add a new tasks.
        while cmd_list and len(next_tasks) < max_num_process:
            cmd = cmd_list.pop()
            next_tasks.append(start_obj(cmd))


        #close tasks (copy finished files to final destination)
        for task in tasks_to_close:
            task.close()
            sys.stdout.write(task.output[-1])
            finished_tasks.append(task.output[-1])

        #start the new loop
        current_tasks = next_tasks


        #display progress
        n_finished = len(finished_tasks)
        n_remaining = len(current_tasks) + len(cmd_list)
        progress_str = 'Tasks: {} finished, {} remaining. Total_time {}.'.format(
            n_finished, n_remaining, total_timer.get_time_str())

        print('*************************************************')
        print(progress_str)
        print('*************************************************')

    #if i don't add this the GUI could terminate before displaying the last text.
    sys.stdout.flush()
    time.sleep(1)


def cmdlist2str(cmdlist):
    # change the format from the list accepted by Popen to a text string
    # accepted by the terminal
    for ii, dd in enumerate(cmdlist):
        if not dd.startswith('-'):
            if os.name != 'nt':
            	dd = "'" + dd + "'"
            else:
                if dd.endswith(os.sep):
                    dd = dd[:-1]
                dd = '"' + dd + '"'

        if ii == 0:
            cmd_str = dd
        else:
            cmd_str += ' ' + dd
    return cmd_str


def print_cmd_list(cmd_list_compress):
    # print all the commands to be processed
    if cmd_list_compress:
        for cmd in cmd_list_compress:
            cmd_str = cmdlist2str(cmd)
            print(cmd_str)
