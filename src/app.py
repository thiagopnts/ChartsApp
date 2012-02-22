#!/usr/bin/python

import sys
from tkFileDialog import askopenfilename
from matplotlib import pyplot as plt
from random import random
from Tkinter import Tk

class Chart:
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    gray = '#687B74'
    

    def __init__(self, act, time):
        fig = plt.figure()
        ax = fig.add_subplot(211)
        dim = 5

        for times in act.values():
            color = self.colors.pop(int(random()*len(self.colors)-1))
            bars = [(t[0], (t[0]-t[1])*-1) for t in times]
            facecolors = [color for i in range(len(bars)-1)]
            facecolors.insert(0, self.gray)
            ax.broken_barh(bars, (dim,2), facecolors=facecolors)
            dim += 5

        #limite do eixo Y
        ax.set_ylim(0, 35) 

        #limite do eixo X (definido pelo tempo de execucao dos modulos
        ax.set_xlim(time[0], time[1])

        ax.set_xlabel('Tempo de execucao ----->')

        ax.set_yticks([6,11])
        ax.set_yticklabels(act.keys())


        ax.grid(True)
        plt.title('Analise dos modulos')
        plt.show()

class Reader:
    __apps = []

    def __init__(self, path=None):
        self.file = open(path, "r")
        self.log = self.file.readlines()
        self__apps = self.get_apps()
    
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
        start = int(self.log[0].split(',')[2].split(' ')[0].replace('.',''))
        end = int(self.log[len(self.log)-1].split(',')[2].split(' ')[0].replace('.',''))

        return (start, end)

    #deprecated
    def get_apps_activy(self):
        activity = {}
        for app in self.__apps:
            running = False
            activity[app] = []
            for line in self.log:
                line = line.split(',')
                stat = line[0]
                name = self.treat_name(line[1])
                time = self.treat_time(line[2])
                if stat != 'ON' and stat != 'OFF' and name != 'confManager':
                    if app == name and not running:
                        if not activity[app].count(time):
                            activity[app].append(time)
                            running = True
                    else:
                        if running and name != app:
                            if not activity[app].count(time):
                                activity[app].append(time)
                                running = False
                if running and name != app:
                    if not activity[app].count(time):
                        activity[app].append(time)
        return activity

    #deprecated
    def get_info(self):
        activy = {}
        for app in self.__apps:
            activy[app] = []
            log = self.log
            for i in range(len(log)):
                line = log[i].split(',')
                status = line[0].lower()
                current = self.treat_name(line[1])
                time = self.treat_time(line[2])
                if app == current and status == 'read' or status =='write':
                    if len(activy[app]) == 0:
                        activy[app].append((time,))
                    else:
                        activy[app].append(activy[app].pop().__getslice__(0,1)+(time,))
        print activy

    def treat_time(self, time):
        return int(time.split(' ')[0].replace('.', ''))

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

    print activities

    chart = Chart(activities, time)
