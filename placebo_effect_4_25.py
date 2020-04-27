# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 21:15:38 2020

@author: kevin
"""

import matplotlib.pyplot as plt
import random
import numpy as np
N=100
sample_size=50
generation=500
repeat=10


percent_T1=0.9 #starting percentage of individual with technology T1
Eb1=0.3
Eb2=0.4
beta=0.0
beta1=0.0

w_o=1
w_a=1

def equi_effi(Eb,beta,beta1):
    return Eb/(1-Eb*beta1-beta)
def realized_eff(Eb,p,beta,beta1):
    return Eb+p*beta+Eb*p*beta1
def belief(ind,T): #individual's subjective belief in T
    return 
def T_freq(T,pop):
    T1_num=0
    T2_num=0
    for i in pop:
        if i[0]=="T1":
            T1_num=T1_num+1
        else:
            T2_num=T2_num+1
    if T=="T1":
        return T1_num/N
    if T=="T2":
        return T2_num/N

T1_fix_num=0
T2_fix_num=0
no_fix_num=0
for re in range(repeat):
    pop=[]
    #construct population
    for i in range(N):
        if random.random()<percent_T1:
            pop.append(["T1",equi_effi(Eb1, beta, beta1)])
        else:
            pop.append(["T2",0])#T2 being the new technology, individual's initial belief in it is 0
    
    
    T1_freq_time_series=[]
    for gen in range(generation):
        pop_f1=[]
        for i in range(N):
            model_list_temp=[]
            for j in range(sample_size):
                model_list_temp.append(pop[random.randint(0,N-1)])    
            model_list=[]
            for q in model_list_temp:#compute realized outcome
                if q[0]=="T1":
                    if realized_eff(Eb1, q[1], beta, beta1)>random.random():
                        model_list.append([q[0],q[1],"pos"])
                    else:
                        model_list.append([q[0],q[1],"neg"])
                else:
                    if realized_eff(Eb2, q[1], beta, beta1)>random.random():
                        model_list.append([q[0],q[1],"pos"])
                    else:
                        model_list.append([q[0],q[1],"neg"])
            #now individual i has a model_list
            #and will construct their belief regarding the efficacy of the two technologies
                #first check the frequency of T1 and T2 in models
                #second check the realized efficacy of T1 and T2:
            T1_count=0
            T2_count=0
            T1_pos_count=0
            T1_neg_count=0
            T2_pos_count=0
            T2_neg_count=0
            
            for k in model_list:
                if k[0]=="T1":
                    T1_count=T1_count+1
                    if k[2]=="pos":
                        T1_pos_count=T1_pos_count+1
                    else:
                        T1_neg_count=T1_neg_count+1
                if k[0]=="T2":
                    T2_count=T2_count+1
                    if k[2]=="pos":
                        T2_pos_count=T2_pos_count+1
                    else:
                        T2_neg_count=T2_neg_count+1
                    
            if T1_count==0: #if there's no T1 in model_list
                belief_T2=(w_o*T2_count+w_a*T2_pos_count)/(w_o*T2_count+w_a*T2_pos_count+w_a*T2_neg_count)
                pop_f1.append(["T2",belief_T2])
            elif T2_count==0:
                belief_T1=(w_o*T1_count+w_a*T1_pos_count)/(w_o*T1_count+w_a*T1_pos_count+w_a*T1_neg_count)
                pop_f1.append(["T1",belief_T1])
            else: #when there's both T1 and T2 in the model sample
                belief_T1=(w_o*T1_count+w_a*T1_pos_count)/(w_o*T1_count+w_o*T2_count+w_a*T1_pos_count+w_a*T1_neg_count)
                belief_T2=(w_o*T2_count+w_a*T2_pos_count)/(w_o*T1_count+w_o*T2_count+w_a*T2_pos_count+w_a*T2_neg_count)
                if belief_T1/(belief_T1+belief_T2)>random.random():
                    pop_f1.append(["T1",belief_T1])
                else:
                    pop_f1.append(["T2",belief_T2])
        pop=pop_f1
        T1_freq_time_series.append(T_freq("T1",pop))
    print ("T1_freq=",T_freq("T1",pop), "T2_freq=",T_freq("T2",pop))
    if T_freq("T1",pop)==1:
        T1_fix_num=T1_fix_num+1
    elif T_freq("T2",pop)==1:
        T2_fix_num=T2_fix_num+1
    else:
        no_fix_num=no_fix_num+1
        
    
    gen_list=[i for i in range(generation)]
    plt.plot (gen_list,T1_freq_time_series,color="k")
    plt.xlabel("Generation", fontsize=14)
    plt.ylabel("T1 frequency")

        
print ("T1_fix_rate=",T1_fix_num/repeat,"T2_fix_rate=",T2_fix_num/repeat,"no_fix_rate=",no_fix_num/repeat)
        
        
        
        
        
        
        
        