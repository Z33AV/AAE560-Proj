#import libraries
import matplotlib.pyplot as plt
import csv
import numpy as np

#GLOBAL parameters
root_path = "./560_Project_Runs/"
run_name = "Run_1/"
ledger_name = "ledger.csv"
t_fold = "Transporters/"
fn_fold = "Fixed_Nodes/"
vn_fold = "Variable_Nodes/"

#dataloading functions
def readTransporter(t_id):
    with open(root_path+run_name+t_fold+t_id+".csv") as f:
        tlist = []
        reader = csv.reader(f, delimiter=",")
        for item in reader:
            tlist.append(item)
        f.close()
    return tlist

def fixedNodeAnalysis(n_id):
    with open(root_path+run_name+fn_fold+n_id+".csv") as f:
        fnlist = []
        reader = csv.reader(f, delimiter=",")
        for item in reader:
            fnlist.append(item)
        f.close()
    return fnlist

def variableNodeAnalysis(n_id):
    with open(root_path+run_name+vn_fold+n_id+".csv") as f:
        fnlist = []
        reader = csv.reader(f, delimiter=",")
        for item in reader:
            fnlist.append(item)
        f.close()
    return fnlist

#plotting functions
def plotTransporters(t_ids, cat):
    plt.title(cat+" vs Time for Transporters")
    plt.xlabel("Time")
    plt.ylabel(cat)

    #plot for all transporters
    for tid in t_ids:
        data = np.array(readTransporter(tid))
        ind = np.where(data[0, :] == cat)[0]
        data = np.delete(data, (0), axis=0)
        tmpx = data[:, 0]
        tmpy = data[:, ind]
        plt.plot(tmpx.astype(float), tmpy.astype(float), label=cat)
    
    plt.legend()
    print("Show Plot")
    plt.show()

def plotFNodes(n_ids, cat):
    plt.title(cat+" vs Time for Fixed Nodes")
    plt.xlabel("Time")
    plt.ylabel(cat)

    #plot for all transporters
    for nid in n_ids:
        data = np.array(readTransporter(nid))
        ind = np.where(data[0, :] == cat)[0]
        data = np.delete(data, (0), axis=0)
        tmpx = data[:, 0]
        tmpy = data[:, ind]
        plt.plot(tmpx.astype(float), tmpy.astype(float), label=cat)
    
    plt.legend()
    plt.show()

def plotVNodes(n_ids, cat):
    plt.title(cat+" vs Time for Variable Nodes")
    plt.xlabel("Time")
    plt.ylabel(cat)

    #plot for all transporters
    for nid in n_ids:
        data = np.array(readTransporter(nid))
        ind = np.where(data[0, :] == cat)[0]
        data = np.delete(data, (0), axis=0)
        tmpx = data[:, 0]
        tmpy = data[:, ind]
        plt.plot(tmpx.astype(float), tmpy.astype(float), label=cat)
    
    plt.legend()
    plt.show()
