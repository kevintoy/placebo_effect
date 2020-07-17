# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 21:43:40 2020

@author: kevin
"""

#Note: This update first calculates the starting belief in T1 by running a function (updated 6_23_2020)
#and then simulates the invasion of T2. 

import time
start_time = time.time()

from itertools import product
import pandas

import matplotlib.pyplot as plt
import random
import numpy as np
from scipy import stats

N=200

sample_size=5
final_round_sample_size=5

generation=200
repeat=500

percent_T1=0.995 #starting percentage of individual with technology T1
belief_formation="mean" #individuals can either "sample" from a beta distribution or 
                          #just use the mean of the beta distribution. Possible arguments: "mean", "sample"
model_selection="False" #whether there will be a second round of sampling where models in the first round
                        #with positive outcomes are more likely to be selected
pos_fit=1
neg_fit=1

prior_a1=1
prior_b1=1
prior_a2=1
prior_b2=1

Eb1=0.3
Eb2=0.5
beta=0.3
beta1=0.3

w_o=1
w_a=1
w_action=1



def realized_eff(Eb,p,beta,beta1):
    return Eb+p*beta+Eb*p*beta1

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
    
def T_ave_belief(T,pop):
    belief_sum_T1=0
    belief_sum_T2=0
    for i in pop:
        if i[0]=="T1":
            belief_sum_T1=belief_sum_T1+i[1]
        else:
            belief_sum_T2=belief_sum_T2+i[1]
    if T=="T1":
        return belief_sum_T1/N
    if T=="T2":
        return belief_sum_T2/N
    
#first, calculate T1_ini_belief:

def ini_T1_belief(beta=beta, beta1=beta1, Eb=Eb1, w_action=w_action):
    Er_equi=(w_action*(Eb+beta+beta1*Eb)+Eb)/(w_action+(1-beta-beta1*Eb))
    belief_equi=(w_o+Er_equi*w_a)/(w_o+w_a)
    return belief_equi

#this main function takes T1_ini_belief as an argument
def main(beta,beta1,Eb2,w_o,sample_size):
    timer=0
    T1_fix_num=0
    T2_fix_num=0
    no_fix_num=0
    
    T1_end_freq_list=[]
    
    global T1_repeat_ave
    global T2_repeat_ave
    T1_repeat_ave=[]
    T2_repeat_ave=[]
    for re in range(repeat):
        pop=[]
        #construct population
        T1_belief=ini_T1_belief(beta, beta1, Eb1, w_o)# w_o here is "observed action"
        
        #set up the initial population in a deterministic way
        for i in range(int(N*percent_T1)):
            pop.append(["T1",T1_belief])
            
        for i in range(int(N*(1-percent_T1))):
            pop.append(["T2",0])
        
        
        T1_freq_time_series=[]
        T1_ave_belief_series=[]
        T2_ave_belief_series=[]
        for gen in range(generation):
            pop_f1=[]
            for i in range(N): #here i represent a individual
                model_list_temp=[]
                for j in range(int(sample_size)):
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
                if model_selection=="True": #here, naive agents are doing a second round of model selection
                                            #by selecting the final round of models according to their weight of pos/neg outcomes
                    #now attaching a pos/neg weight as the 3rd element in each model vecter
                    for r in model_list:
                        if r[2]=="pos":
                            r.append(pos_fit)
                        if r[2]=="neg":
                            r.append(neg_fit)
                                          
                    p_weight_list=[]
                    
                    for ind in model_list:
                        p_weight_list.append(ind[3])
                    p_weight_list_normalized=[]
                    for weight in p_weight_list: #normalize weight list
                        p_weight_list_normalized.append(weight/sum(p_weight_list))
                    #now pick the index of the model in the first round to be included in the second round
                    final_model_index_list=[]
                    for model in range(final_round_sample_size):
                        final_model_index_list.append(np.random.choice(range(len(model_list)),size=None,p=p_weight_list_normalized,replace=True))
                    final_model_list=[]
                    for index in final_model_index_list:
                        final_model_list.append(model_list[index])
                        
                    
                    model_list=final_model_list        
                            
                            
                            
                            
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
                    if belief_formation=="mean":
                        belief_T2=(w_o*T2_count+w_a*T2_pos_count)/(w_o*T2_count+w_a*T2_pos_count+w_a*T2_neg_count)
                    if belief_formation=="sample":
                        belief_T2=np.random.beta(prior_a2+w_o*T2_count+w_a*T2_pos_count,prior_b2+w_a*T2_neg_count)
                    pop_f1.append(["T2",belief_T2])
                elif T2_count==0: #if there's no T2 in model_list
                    if belief_formation=="mean":    
                        belief_T1=(w_o*T1_count+w_a*T1_pos_count)/(w_o*T1_count+w_a*T1_pos_count+w_a*T1_neg_count)
                    if belief_formation=="sample":
                        belief_T1=np.random.beta(prior_a1+w_o*T1_count+w_a*T1_pos_count,prior_b1+w_a*T1_neg_count)
                    pop_f1.append(["T1",belief_T1])
                else: #when there's both T1 and T2 in the model sample
                    if belief_formation=="mean":    
                    
                        belief_T1=(w_o*T1_count+w_a*T1_pos_count)/(w_o*T1_count+w_o*T2_count+w_a*T1_pos_count+w_a*T1_neg_count)
                        belief_T2=(w_o*T2_count+w_a*T2_pos_count)/(w_o*T1_count+w_o*T2_count+w_a*T2_pos_count+w_a*T2_neg_count)
                    
                        
                        if belief_T1/(belief_T1+belief_T2)>random.random():
                            pop_f1.append(["T1",belief_T1])
                        else:
                            pop_f1.append(["T2",belief_T2])
                    if belief_formation=="sample":
                        belief_T1=np.random.beta(prior_a1+w_o*T1_count+w_a*T1_pos_count,prior_b1+w_o*T2_count+w_a*T1_neg_count)
                        belief_T2=np.random.beta(prior_a2+w_o*T2_count+w_a*T2_pos_count,prior_b2+w_o*T1_count+w_a*T2_neg_count)
                        if belief_T1/(belief_T1+belief_T2)>random.random():
                            pop_f1.append(["T1",belief_T1])
                        else:
                            pop_f1.append(["T2",belief_T2])        
                            
            pop=pop_f1
            T1_freq_time_series.append(T_freq("T1",pop))
            T1_ave_belief_series.append(T_ave_belief("T1", pop))
            T2_ave_belief_series.append(T_ave_belief("T2", pop))
        #print ("T1_freq=",T_freq("T1",pop), "T2_freq=",T_freq("T2",pop))
        T1_repeat_ave.append(T1_ave_belief_series)
        T2_repeat_ave.append(T2_ave_belief_series)
            
        
        if T_freq("T1",pop)==1:
            T1_fix_num=T1_fix_num+1
        elif T_freq("T2",pop)==1:
            T2_fix_num=T2_fix_num+1
        else:
            no_fix_num=no_fix_num+1
        T1_end_freq_list.append(T_freq("T1", pop))
        
        gen_list=[i for i in range(generation)]
        #plt.plot (gen_list,T1_freq_time_series,color="k",linewidth=0.5)
        #plt.xlabel("Generation", fontsize=14)
        #plt.ylabel("T1 frequency")
        #plt.ylim(0,1)
        #plt.ylabel("average belief")
        #plt.plot (gen_list,T1_ave_belief_series,color="b",label="average belief in T1")
        #plt.plot (gen_list,T2_ave_belief_series,color="r",label="average belief in T2")
        #plt.legend()
        timer=timer+1
        print ("repeat=", timer)
    global T1_fix_rate;T1_fix_rate=T1_fix_num/repeat; 
    global T2_fix_rate;T2_fix_rate=T2_fix_num/repeat; 
    global no_fix_rate;no_fix_rate=no_fix_num/repeat; 
    global T1_ave_freq;T1_ave_freq=sum(T1_end_freq_list)/repeat; 
    global T1_SE;T1_SE=stats.sem(T1_end_freq_list);
    
    
    print ("T1_fix_rate=",T1_fix_num/repeat,"T2_fix_rate=",T2_fix_num/repeat,"no_fix_rate=",no_fix_num/repeat)
    #print ("T1_ave_freq=",sum(T1_end_freq_list)/repeat, "SE=", stats.sem(T1_end_freq_list))
    print ("beta=",beta, "beta1=",beta1, "Eb2=",Eb2)



beta_set=[0.5]

Eb2_set=[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
w_o_set=[0.1,0.5,1]
sample_size_set=[2,5,10]

df = pandas.DataFrame.from_records( list( i for i in product(beta_set, Eb2_set, w_o_set, sample_size_set ) ) , 
                                   columns=['beta', 'Eb2', 'w_o', 'n'] )

output_mean=[]
output_se=[]
timer=0

for i in range(len(df)):
    row_list=list(df.loc[i,:])
    main(float(row_list[0]),float(row_list[0]) ,float(row_list[1]),float(row_list[2]),int(row_list[3]))
    
    output_mean.append(T1_ave_freq)
    output_se.append(T1_SE)
    print ("timer=", timer)
    timer=timer+1
df["output_mean"]=output_mean
df["output_se"]=output_se
import csv 
df.to_csv ('test_cluster.csv')
print("--- %s seconds ---" % (time.time() - start_time))
print("generation=",generation)
print("percent_T1=",percent_T1)
print("Eb1=",Eb1)
print("N=",N)



