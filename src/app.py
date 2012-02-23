#!/usr/bin/python

import sys
from tkFileDialog import askopenfilename
from matplotlib import pyplot as plt
from matplotlib.pyplot import legend
from matplotlib.patches import Rectangle
from random import random
from Tkinter import Tk

class Chart:
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    gray = '#687B74'
    

    def __init__(self, act, time):
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

        #limite do eixo Y
        ax.set_ylim(0, 35) 
        #limite do eixo X (definido pelo tempo de execucao dos modulos
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
        self.log = self.file.readlines()
        self__apps = self.get_apps()
    
    def to_centiseconds(self,ms):
        if ms.count('.'):
            l = list(ms)
            i = l.index('.')
            l.pop(i)
            l.insert(i-1, '.')
            l = l.__getslice__(0, len(l)-2)
            return ''.join(l)
        return ms

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

    activities = {} 

    for app in apps:
        if not activities.has_key(app):
            activities[app] = []
        activities[app].append(reader.execution_from(app))
        for tup in reader.activity_from(app):
            activities[app].append(tup)

    print time
    chart = Chart(activities, time)
