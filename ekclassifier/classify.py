#!/usr/bin/env/ python
# -*- coding: utf-8 -*-
# input:      train and test splits
# output:     training Random Forest classifier with subsets of given features (e.g. 14 here),
#             each iteration represents an ablation test (remove a feature, train and test),
#             GLOBAL represents globally optimum set of features
# to execute: python classify.py

# dependencies:
# python -m pip install --upgrade pip
# (sudo) pip install --user numpy scipy
# (sudo) apt-get install python python-tk
# (sudo) pip install -U scikit-learn

#
from __future__ import print_function, division

import os
import scipy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#import plotly
#from plotly.graph_objs import *
#from plotly.offline import download_plotlyjs, init_notebook_mode, iplot

from sklearn import preprocessing, metrics
from sklearn import cross_validation
from sklearn.cross_validation import train_test_split, cross_val_score, cross_val_predict
from sklearn.metrics import classification_report, accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
#from sklearn.neural_network import MLPClassifier
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from scipy.stats.distributions import randint

global_max = 0.0
global_feats = []
global_report = ""


def initialise_all_data(in_file, fts):
    # Import the data and explore the first few rows
    data  = pd.read_csv(in_file, sep=",")
    #print(data.describe())
    header = []
    for item in fts:
        header.append(data.columns.values[item])
    data.head()
    #data.iloc[np.random.permutation(len(data))]
    # Convert to numpy array and check the dimensionality
    npArray = np.array(data)
    #np.random.shuffle(npArray)
    #print(npArray.shape)

    ###Split the data into input features, X, and outputs, y
    # Split to input matrix X and class vector y
    c = npArray[:,0]
    #X = npArray[:,1:-1]
    #take different features into account
    #X = npArray[:,ft:ft+1]
    X = np.empty([len(npArray), len(fts)])
    for index in range(0,len(npArray)):
        for item in range(0, len(fts)):
            X[index, item] = npArray[index, fts[item]]
    y = npArray[:,-1].astype(int)
    # Print the dimensions of X and y
    #print("X dimensions:", X.shape)
    #print("y dimensions:", y.shape)

    # Print the y frequencies
    yFreq = scipy.stats.itemfreq(y)
    #print(yFreq)
    # Convert to numeric and print the y frequencies
    le = preprocessing.LabelEncoder()
    y = le.fit_transform(y)
    yFreq = scipy.stats.itemfreq(y)
    #print(yFreq)
    corr_class = float(yFreq[0,1])
    err_class = float(yFreq[1,1])
    baseline = (corr_class/(corr_class + err_class))
    #print("Baseline (correct instances) = " + str(round(baseline, 4)))
         
    # Auto-scale the data
    #X = preprocessing.scale(X)
    #X = preprocessing.normalize(X)
    
    return X, y, header, c
    
def plot(X):
    # Create a boxplot of the raw data
    nrow, ncol = X.shape
    data = [ Box(
            y = X[:,i],        # values to be used for box plot
            name = header[i],  # label (on hover and x-axis)
            marker = dict(color = "purple"),
        ) for i in range(ncol)
    ]
    layout = Layout(
        xaxis = dict(title = "Feature"),
        yaxis = dict(title = "Value"),
        showlegend=False
    )
    fig = dict(data = data, layout = layout)
    #iplot(fig)
    plotly.offline.plot(fig)

def split(X, y):    
    # Split into training and test sets
    XTrain, XTest, yTrain, yTest = train_test_split(X, y, random_state=1)
    # Print the dimensionality of the individual splits
    print("XTrain dimensions: ", XTrain.shape)
    print("yTrain dimensions: ", yTrain.shape)
    print("XTest dimensions: ", XTest.shape)
    print("yTest dimensions: ", yTest.shape)
    # Calculate the frequency of classes in yTest
    yFreq = scipy.stats.itemfreq(yTest)
    print(yFreq)
    return XTrain, XTest, yTrain, yTest
    
    
def kNN_class(XTrain, XTest, yTrain, yTest, header, nns, wgt):
    ### Apply KNN classification algorithm with scikit-learn
    knn = KNeighborsClassifier(n_neighbors=nns, weights = wgt)
    knn.fit(XTrain, yTrain)
    yPredK = knn.predict(XTest)
    print("Overall Accuracy:", round(metrics.accuracy_score(yTest, yPredK), 2))
    
    ### Calculate validation metrics for your classifier
    # Get the confusion matrix for your classifier using metrics.confusion_matrix
    mat = metrics.confusion_matrix(yTest, yPredK)
    print(mat)
    # Report the metrics using metrics.classification_report
    print(metrics.classification_report(yTest, yPredK))
    print("accuracy: ", round(metrics.accuracy_score(yTest, yPredK), 2))
    
    ### Plot the decision boundaries for different models
    # Check the arguments of the function
    #help(visplots.knnDecisionPlot)
    # Visualise the boundaries
    #visplots.knnDecisionPlot(XTrain, yTrain, XTest, yTest, header, 3, "uniform")      

def grid_search(XTrain, XTest):
    # Create the dictionary of given parameters
    n_neighbors = np.arange(1, 51, 2)
    weights     = ['uniform','distance']
    parameters  = [{'n_neighbors': n_neighbors, 'weights': weights}]
    # Optimise and build the model with GridSearchCV
    gridCV = GridSearchCV(KNeighborsClassifier(), parameters, cv=10)
    gridCV.fit(XTrain, yTrain)
    # Report the optimal parameters
    bestNeighbors = gridCV.best_params_['n_neighbors']
    bestWeight    = gridCV.best_params_['weights']
    print("Best parameters: n_neighbors=", bestNeighbors, "and weight=", bestWeight)

def dt_class(XTrain, XTest, yTrain, yTest):
    dtc = DecisionTreeClassifier()
    dtc.fit(XTrain, yTrain)
    predDT = dtc.predict(XTest)
    mat = metrics.confusion_matrix(yTest, predDT)
    print(mat)
    print(metrics.classification_report(yTest, predDT))
    print("Overall Accuracy:", round(metrics.accuracy_score(yTest, predDT),2))
    #clf = DecisionTreeClassifier(random_state=0)
    #print(cross_val_score(clf, X, y, cv=10))

def rf_class(XTrain, XTest, yTrain, yTest):
    # Build a Random Forest classifier with 100 decision trees
    rf = RandomForestClassifier(n_estimators=100, random_state=0)
    rf.fit(XTrain, yTrain)
    predRF = rf.predict(XTest)
    print (yTest)
    print (predRF)
    mat = metrics.confusion_matrix(yTest, predRF)
    #print(mat)
    #print(metrics.classification_report(yTest, predRF))
    #print("Overall Accuracy:", round(metrics.accuracy_score(yTest, predRF),4))
    report = metrics.classification_report(yTest, predRF)
    voc = report.split("\n")
    out = str(round(metrics.accuracy_score(yTest, predRF),4)) + "\t"
    for item in voc:
        if item.strip().startswith("0"):
            voc1 = item.split("      ")
            out += voc1[2].strip() + "\t" + voc1[3].strip() + "\t" + voc1[4].strip() + "\t"
        if item.strip().startswith("1"):
            voc1 = item.split("      ")
            out += voc1[2].strip() + "\t" + voc1[3].strip() + "\t" + voc1[4].strip()
    #print(out)
    return out

    # Conduct a grid search with 10-fold cross-validation using the dictionary of parameters
    ##n_estimators = np.arange(1, 30, 5)
    ##max_depth = np.arange(1, 100, 5)
    # Also, you may choose any of the following
    # max_features = [1, 3, 10]
    # min_samples_split = [1, 3, 10]
    # min_samples_leaf  = [1, 3, 10]
    # bootstrap = [True, False]
    # criterion = ["gini", "entropy"]
    ##parameters   = [{'n_estimators': n_estimators, 'max_depth': max_depth}]
    ##gridCV = GridSearchCV(RandomForestClassifier(), param_grid=parameters, cv=10)
    ##gridCV.fit(XTrain, yTrain)
    # Print the optimal parameters
    ##best_n_estim      = gridCV.best_params_['n_estimators']
    ##best_max_depth    = gridCV.best_params_['max_depth']
    ##print ("Best parameters: n_estimators=", best_n_estim,", max_depth=", best_max_depth)
    ##clfRDF = RandomForestClassifier(n_estimators=best_n_estim, max_depth=best_max_depth)
    ##clfRDF.fit(XTrain, yTrain)
    ##predRF = clfRDF.predict(XTest)
    ##print (metrics.classification_report(yTest, predRF))
    ##print ("Overall Accuracy:", round(metrics.accuracy_score(yTest, predRF),2))


def nb_class(XTrain, XTest, yTrain, yTest):
    nb = GaussianNB()
    nb.fit(XTrain, yTrain)
    predNB = nb.predict(XTest)
    mat = metrics.confusion_matrix(yTest, predNB)
    #print(mat)
    #print(metrics.classification_report(yTest, predNB))
    #print("Overall Accuracy:", round(metrics.accuracy_score(yTest, predNB),4))
    report = metrics.classification_report(yTest, predNB)
    voc = report.split("\n")
    out = str(round(metrics.accuracy_score(yTest, predNB),4)) + "\t"
    for item in voc:
        if item.strip().startswith("0"):
            voc1 = item.split("      ")
            out += voc1[2].strip() + "\t" + voc1[3].strip() + "\t" + voc1[4].strip() + "\t"
        if item.strip().startswith("1"):
            voc1 = item.split("      ")
            out += voc1[2].strip() + "\t" + voc1[3].strip() + "\t" + voc1[4].strip()
    #print(out)
    return out



#to automatically populate feature list with features
def populate_feature_list(rng, to_exclude):
    f_list = []
    for i in range(1, rng):
        if not i in to_exclude:
            f_list.append(i)
    return f_list


#get report with the performance metrics and feature list
#and analyse exclusion of what feature brings the best performance
#return the feature in the to_exlude list
#metric = metric to optimise, given with its index, e.g., 0 for accuracy
#rng = for the range of features, e.g. 130 from the beginning
def grid_search(rng, to_exclude, metric):
    global global_max
    global global_feats
    global global_report
    features = populate_feature_list(rng, to_exclude)
    if (len(features)>1):
        print("Populated")
        a_max = 0.0
        feature = 0
        for odd_one in features:
            feats1 = []
            for feat in features:
                if not feat == odd_one:
                    feats1.append(feat)
            print(str(odd_one) + ": Training with " + str(len(features)) + " features....")
            XTrain, yTrain, header, cTrain = initialise_all_data("splits1/train5.csv", feats1) 
            XTest, yTest, header, cTest = initialise_all_data("splits2/test5_1k.csv", feats1)
            report = rf_class(XTrain, XTest, yTrain, yTest)
            voc = report.split("\t")
            #acc pc rc fc pe re fe
            if float(voc[metric])>a_max:
                a_max = float(voc[metric])
                feature = odd_one
                print(a_max)

        #############################
        to_exclude.append(feature)
        new_features = populate_feature_list(rng, to_exclude)
        print(new_features)
        print(a_max)
        XTrain, yTrain, header, cTrain = initialise_all_data("splits1/train5.csv", new_features) 
        XTest, yTest, header, cTest = initialise_all_data("splits2/test5_1k.csv", new_features)
        report = rf_class(XTrain, XTest, yTrain, yTest)
        print(report)
        #############################
        if (global_max<=a_max):
            global_max = a_max
            global_feats = new_features
            global_report = report
        #############################
        print("######\nGLOBAL:")
        print(global_max)
        print(global_feats)
        print(global_report)
        print("######\n")

        while (len(features)>2):
            #run recursively
            grid_search(rng, to_exclude, metric)
            break




def analyse_outputs(path, files, output):
    out = open(output, "w")
    a_dict = {}
    for a_file in files:
        f = open(path + a_file)
        for a_line in f.readlines():
            a_dict[a_line.strip()] = a_dict.get(a_line.strip(), 0) + 1
        f.close()
    for key in sorted(a_dict.keys()):
        if a_dict.get(key)>(len(files)-4):
            out.write(key + "\n")
    out.close()
    
    
if __name__ == "__main__":
    grid_search(15, [], 0)