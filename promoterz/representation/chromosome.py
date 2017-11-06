#!/bin/python
from deap import base
from deap import creator
from deap import tools

from copy import deepcopy
import random

from .. import functions


getPromoterFromMap = lambda x: [x[z] for z in list(x.keys())]

def constructPhenotype(stratSettings, chrconf, Individue):
    Settings = {}
    GeneSize=2
    R = lambda V, lim: (lim[1]-lim[0]) * V/(33*chrconf['GeneSize']) + lim[0]
    PromotersPath = {v: k for k, v in Individue.PromoterMap.items()}
    #print(PromotersPath)
    #print(Individue[:])
    Promoters = list(PromotersPath.keys())

    for C in Individue:
        for BP in range(len(C)):
            if C[BP] in Promoters:
                read_window = C[BP+1:BP+1+GeneSize]
                read_window = [ V for V in read_window if type(V) == int and V < 33 ]
                Value = sum(read_window)
                ParameterName = PromotersPath[C[BP]]

                Value = R(Value, stratSettings[ParameterName])

                Settings[ParameterName] = Value

    _Settings = functions.expandNestedParameters(Settings)
    Settings = {Individue.Strategy: _Settings}

    return Settings

def getToolbox(genconf, Attributes):
    toolbox = base.Toolbox()
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax,
                   PromoterMap=None, Strategy=genconf.Strategy)

    toolbox.register("mate", functions.pachytene)
    toolbox.register("mutate", functions.mutate)

    PromoterMap = initPromoterMap(Attributes)
    toolbox.register("newind", initInd, creator.Individual, PromoterMap, genconf.chromosome)
    toolbox.register("population", tools.initRepeat, list, toolbox.newind)

    toolbox.register("constructPhenotype", constructPhenotype, Attributes, genconf.chromosome)
    return toolbox

def initPromoterMap(ParameterRanges):
    PRK = list(ParameterRanges.keys())

    Promoters = [ x for x in PRK ]
    space = list(range(120,210))
    random.shuffle(space)

    PromoterValues = [ space.pop() for x in Promoters ]
    PromoterMap = dict(zip(Promoters, PromoterValues))


    print(ParameterRanges)
    print(PromoterMap)
    assert(len(PRK) == len(list(PromoterMap.keys())))
    return PromoterMap

def initChromosomes(PromoterMap, chrconf):
    Promoters = getPromoterFromMap(PromoterMap)
    PromoterPerChr = round(len(Promoters)/chrconf['Density'])+1

    _promoters = deepcopy(Promoters)
    Chromosomes = [[] for k in range(PromoterPerChr)]


    while _promoters:
        for c in range(len(Chromosomes)):
            if random.random() < 0.3:
                if _promoters:
                    promoter = _promoters.pop(random.randrange(0,len(_promoters)))
                    Chromosomes[c].append(promoter)
            for G in range(chrconf['GeneSize']):
                Chromosomes[c].append(random.randrange(0, 33))

    return Chromosomes

def initInd(Individual, PromoterMap, chrconf):

    i = Individual()
    i[:] = initChromosomes(PromoterMap, chrconf)
    i.PromoterMap = PromoterMap
    return i

def generateUID():
    Chars = string.ascii_uppercase + string.digits
    UID = ''.join(random.choices(Chars), k=6)
    return UID

def getIndividueMap():
    IndividueMap = {
        'high': generateUID(),
        'low': generateUID(),
        'persistence': generateUID()
        }

    return IndividueMap
