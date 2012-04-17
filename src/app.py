#!/usr/bin/python

import sys
from tkFileDialog import askopenfilename
from matplotlib import pyplot as plt
from matplotlib.pyplot import legend
from matplotlib.patches import Rectangle
from random import random
from Tkinter import Tk
from copy import copy

class Chart:
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    gray = '#687B74'
    

    def __init__(self, act, time):
        self.setup(act, time)

    def setup(self, act, time):
        fig = plt.figure(figsize=(13,7))
        ax = plt.subplot(111)
        dim = 5
        #broken_barh are not supported to create legends so
        #we have to use a proxy artist.
        proxies = []
        labels = []
        proxies.append(ax.plot(0,0,'k:'))
        labels.append('not configured')
        proxies.append(Rectangle((0,0),1,1,fc=self.gray))
        labels.append('idle')
        for times in act.values():
            color = self.colors.pop(int(random()*len(self.colors)-1))
            bars = [(t[0], (t[0]-t[1])*-1) for t in times]
            facecolors = [color for i in range(len(bars)-1)]
            proxies.append(Rectangle((0,0),1,1,fc=color))
            labels.append('running')
            facecolors.insert(0, self.gray)
            ax.broken_barh(bars, (dim,2), facecolors=facecolors)
            dim += 5
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
            box.width, box.height * 0.5])

        legend(proxies, labels, loc='upper center',
                bbox_to_anchor=(0.5, -0.15), ncol=5, fancybox=True, 
                shadow=True)

        ax.set_ylim(0, 35) 

        ax.set_xlim(time[0], time[1])

        ax.set_xlabel('Execution time --->')

        ax.set_yticks([6,11])

        ax.set_yticklabels(act.keys())

        ax.grid(True)

        plt.title("Modules' analysis")
        plt.show()

class Reader:
    __apps = []

    def __init__(self, path=None):
        self.file = open(path, "r")
        header = self.file.readline().split(',')
        self.fpga, self.size = header[1], header[2]
        self.log = self.file.readlines()
        self.modules_info = self.get_modules_info()
        self.__apps = self.get_apps()

    def generate_report(self, acts):
        report = file('report.txt', 'a')

        total_sim = self.get_total_execution_time()[1]
        final_power = 0
        final_percent = 0
        final_on = 0
        for info in self.modules_info:
            total_on = 0
            for i in xrange(1, len(acts[info[0]])):
                module = info[0]
                power = int(info[1])
                percent = self.get_percent(info[2])

                total_on += acts[info[0]][i][1] - acts[info[0]][i][0]
                total_exec = acts[info[0]][0][1] - acts[info[0]][0][0]
                total_idle = total_exec - total_on
                final_power += power
                final_percent += percent
                final_on += total_on
            report.write(module+';'+str(power)+'w;'+str(percent)+'%;'+str(total_exec)+'ms;'+str(total_idle)+'ms;'+str(total_on)+'ms;'+str(total_sim)+'ms\n')
        report.write('TOTAL;'+str(final_power)+'w;'+str(final_on)+'ms;'+str(final_percent)+'%;'+str(total_sim)+'ms\n')
        report.close()
        return report
    
    def get_percent(self, module_size):
        return int(100 * float(module_size)/float(self.size))


    def get_modules_info(self):
        module_info = []
        wrapper = copy(self.log)
        for line in wrapper:
            inf = line.strip().split(',')
            if inf[0] != 'INFO':
                break
            else:
                module_info.append([inf[1],inf[2], inf[3]])
                self.log.remove(line)
        return module_info
    

    def get_file(self):
        return self.log

    def get_apps(self):
        if not len(self.__apps):
            for line in self.log:
                info = line.split(',')
                app = info[1].split('.')[0]
                if app not in self.__apps and app != 'confManager':
                    self.__apps.append(app)
        return self.__apps

    def get_total_execution_time(self):
        start = float(self.log[0].split(',')[2].split(' ')[0])
        end = float(self.log[len(self.log)-1].split(',')[2].split(' ')[0])

        return (start, end)

    def treat_time(self, time):
        return float(time.split(' ')[0])

    def treat_name(self, name):
        return name.split('.')[0]

    def activity_from(self, app):
        log = self.log
        info = {}
        info[app] = []
        info[app].append([])
        count = 0
        for i in range(len(log)):
            line = log[i].split(',')
            status = line[0].lower()
            current_app = self.treat_name(line[1])
            time = self.treat_time(line[2])
            if app == current_app:
                if status == 'read' or status == 'write':
                    info[app][count].append(time)
            else:
                if len(info[app][count]) > 0:
                    count += 1
                    info[app].append([])
        tuples = []
        for list in info[app]:
            if list:
                tuples.append((list.pop(0),list.pop()))
        return tuples

    def execution_from(self, app):
        log = self.log
        times = []
        on = False
        for line in log:
            line = line.split(',')
            status, current_app, time = line[0].lower(), self.treat_name(line[1]), self.treat_time(line[2])
            if app == current_app and status == 'on':
                times.append(time)
                on = True
            if app == current_app and status == 'off' and on:
                times.append(time)
                on = False
                break
        return tuple(times)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        root = Tk()
        root.withdraw()
        file = askopenfilename(parent=root)
        if file:
            reader = Reader(file)
        else:
            print "choose a log!"
    else:
        reader = Reader(sys.argv[1])

    apps = reader.get_apps()
    time = reader.get_total_execution_time()
    print reader.modules_info
    print reader.fpga
    print reader.size
    activities = {} 

    for app in apps:
        if not activities.has_key(app):
            activities[app] = []
        activities[app].append(reader.execution_from(app))
        for tup in reader.activity_from(app):
            activities[app].append(tup)

    reader.generate_report(activities)
    print activities
    print time
    chart = Chart(activities, time)
