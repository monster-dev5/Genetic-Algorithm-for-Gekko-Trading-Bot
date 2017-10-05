#!/bin/python

import os
import datetime
import random
import pandas as pd
from deap import tools
import numpy as np

from gekkoWrapper import runBacktest
from Settings import getSettings

statisticsNames = {'avg': 'Average profit',
                   'std': 'Profit variation',
                   'min': 'Minimum profit',
                   'max': 'Maximum profit'}

def getStatisticsMeter():
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    return stats

def Evaluate(IndividualToSettings, DateRange, Individual):
    # IndividualToSettings(IND, STRAT) is a function that depends on GA algorithm,
    # so should be provided;
    Settings = IndividualToSettings(Individual)
    #print(Settings)
    if not checkPhenotypeIntegrity(Settings, TargetParameters):
        return 0, False

    Profit = runBacktest(Settings, DateRange)
    return Profit, True

def getDateRange(Limits, deltaDays=3):
    DateFormat="%Y-%m-%d %H:%M:%S"

    epochToString = lambda D: datetime.datetime.utcfromtimestamp(D).strftime(DateFormat)
    deltams=deltaDays * 24 * 60 * 60

    DateRange = {
        "from": "%s" % epochToString(Limits['to']-deltams),
        "to": "%s" % epochToString(Limits['to'])
    }
    return DateRange

def getRandomDateRange(Limits, deltaDays, testDays=0):
    DateFormat="%Y-%m-%d %H:%M:%S"

    epochToString = lambda D: datetime.datetime.utcfromtimestamp(D).strftime(DateFormat)
    FLms = Limits['from']
    TLms = Limits['to']
    deltams=deltaDays * 24 * 60 * 60
    testms=testDays * 24 * 60 * 60

    Starting= random.randint(FLms,TLms-deltams-testms)
    DateRange = {
        "from": "%s" % epochToString(Starting),
        "to": "%s" % epochToString(Starting+deltams)
    }

    return DateRange


def stratSettingsProofOfViability(Settings, DatasetLimits):
    AllProofs = []
    for W in range(12):
        DateRange = getRandomDateRange(DatasetLimits, 30)
        q=runBacktest(Settings, DateRange)
        AllProofs.append(q)
        print('Testing monthly profit %.3f' % q)

    iValue = 100
    for W in AllProofs:
        iValue += iValue * (W/100)
    check = [x for x in AllProofs if x > 0]
    Valid = len(check) == len(AllProofs)
    print("Annual profit %.3f%%" % (iValue-100))
    return Valid   
 
def pasteSettingsToUI(Settings):
    text = []
    toParameter = lambda name, value: "%s = %f" % (name,value)
    Strat = list(Settings.keys())[0]
    text.append('{ %s }' % Strat)
    #rint("{{ %s }}" % Settings[Strat])
    Settings = Settings[Strat]
    for W in Settings.keys():
        Q = Settings[W]
        if type(Q) == dict:
            text.append('\n[%s]' % W)
            for Z in Q.keys():
                text.append(toParameter(Z, Q[Z]))
            text.append('')
        else:
            text.append(toParameter(W, Q))
    return '\n'.join(text)

def loadGekkoConfig():
    pass

def logInfo(message, filename="evolution_gen.log"):
    gsettings = getSettings()['global']
    filename = os.path.join(gsettings['save_dir'], filename)
    F=open(filename, 'a+')
    F.write(message)
    print(message)
    F.close()

def write_evolution_logs(i, stats, filename="evolution_gen.csv"):
    #print(i, stats)
    if type(stats) == dict:
        message = ','.join([str(x) for x in [i,stats['avg'],stats['std'],stats['min'],stats['max'], stats['dateRange']]])
    elif type(stats) == list:
        message = ','.join([str(x) for x in [i,stats[1],stats[2],stats[3],stats[4],stats[5]]])
    else:
        raise
    #print(message)
    gsettings = getSettings()['global']
    filename = os.path.join(gsettings['save_dir'], filename)
    if i == 0 and os.path.isfile(filename):
        os.remove(filename)
    f=open(filename, 'a+')
    f.write(message+"\n")
    #print(message)
    f.close()
