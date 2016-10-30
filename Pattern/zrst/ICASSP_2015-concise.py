import asr
# from zrst import pyASR
# from zrst import pySFX
# from zrst import pyEXT
import std
import numpy as np
import scipy.stats as stat
# ######################phase1####################
# generate patterns

# ## set paths ###

dropbox_path = r'D:/Dropbox/'
corpus_path = dropbox_path + r'Semester 8.5/Corpus_5034wav/'
target_path = dropbox_path + r'Semester 12.5/ICASSP 2015 Data/addmix5034/'
#init generated by matlab/clusterDetection.m
initial_path = dropbox_path + r'ULT_v0.2/matlab/IDump_timit_test_50_flatten.txt'
history_path = dropbox_path + r'Semester 9.5/'

S_list = [3, 7, 13]
M_list = [50, 100, 300]
for S in S_list:
    for M in M_list:
        config_name = '5034_' + str(M) + '_' + str(S)
        ### continue interrupted work ###
        # declare object
        A = pyASR.ASR(corpus=corpus_path, target=target_path, nState=S)
        # select interrupted folder
        A.offset = 30
        A.readASR(history_path + str(A.offset) + '_' + config_name)
        # continue for some iterations
        A.iteration('a_mix', config_name)
        A.iteration('a_keep', config_name)
        A.iteration('a_mix', config_name)
        A.iteration('a_keep', config_name)
        A.iteration('a_mix', config_name)
        A.iteration('a_keep', config_name)






#######################phase3####################

# constuct std object
drpbox_path = r'/home/c2tao/Dropbox/'
querie_path = drpbox_path + r'Semester 12.5/ICASSP 2015 Data/5034_query_active/'
labels_path = drpbox_path + r'Semester 12.5/ICASSP 2015 Data/' + r'fa.mlf'
answer_path = drpbox_path + r'Semester 12.5/ICASSP 2015 Data/' + r'querycontent.txt'
corpus_path = drpbox_path + r'Semester 8.5/Corpus_5034wav/'

Q = std.STD(root=querie_path, label=labels_path, qlist=answer_path, corpus=corpus_path)
S_list = [3, 7, 13]
M_list = [50, 100, 300]
K_list = [36, 40]
for S in S_list:
    for M in M_list:
        for K in K_list:
            p_name = str(K) + '_5034_' + str(M) + '_' + str(S)
            A = asr.ASR(target=drpbox_path + r'Semester 9.5/' + p_name + '/')
            Q.add_pattern(A, p_name)

Q.query_init()
Q.query_copy()
Q.query_build()
Q.parse_query()

for p in Q.pattern_list:
    Q.pattern_similarity(p)

sims = {}
#Q.feature_similarity()
for p in Q.pattern_list:
    sims[p] = Q.pattern_similarity(p)

simb = Q.feature_similarity()

import math


def to_relative(myList):
    adjusted = map(lambda x: math.erf(x), np.linspace(0, 1, num=5034))[::-1]
    scoindex = [i[0] for i in sorted(enumerate(myList), key=lambda x: x[1])]
    return [adjusted[scoindex[i]] for i in range(len(myList))]


similarity0 = {}
similarity1 = {}
similarity2 = {}
for q in range(len(Q.query_answer)):
    similarity0[q] = -np.array(simb[q])
    similarity1[q] = np.zeros(5034)
    similarity2[q] = np.zeros(5034)
    for p in Q.pattern_list:
        if "36" in p:
            similarity1[q] += np.exp(-np.array(sims[p][q]) / 100.0)
            #similarity1[q] += to_relative(np.array(sims[p][q]))
        elif "40" in p:
            similarity2[q] += np.exp(-np.array(sims[p][q]) / 100.0)
            #similarity2[q] -= np.array(sims[p][q])
            #similarity2[q] += to_relative(np.array(sims[p][q]))

L0 = Q.mean_average_precision(similarity0)
L1 = Q.mean_average_precision(similarity1)
L2 = Q.mean_average_precision(similarity2)

Li = sorted(range(52), key=lambda x: L1[x] - L2[x])

for kkk in range(52):
    print np.mean([L2[i] for i in Li[:kkk]]) - np.mean([L1[i] for i in Li[:kkk]]), np.mean(
        [L1[i] for i in Li[:kkk]]), np.mean([L2[i] for i in Li[:kkk]])

cutoff = 52
print np.mean([L0[i] for i in Li[:cutoff]])
print np.mean([L1[i] for i in Li[:cutoff]])
print np.mean([L2[i] for i in Li[:cutoff]])

S_list = [3, 7, 13]
M_list = [50, 100, 300]
K_list = [36, 40]

a_list = []
b_list = []
for S in S_list:
    for M in M_list:
        for K in K_list:
            similarity = {}
            p = str(K) + '_5034_' + str(M) + '_' + str(S)
            for q in range(len(Q.query_answer)):
                similarity[q] = -1.0 * np.array(sims[p][q])
            pv = np.mean([(Q.mean_average_precision(similarity))[i] for i in Li[:cutoff]])
            if K == 36:
                a_list += pv,
            else:
                b_list += pv,


#ttest_1samp(a, popmean[, axis]) Calculates the T-test for the mean of ONE group of scores.
#ttest_ind(a, b[, axis, equal_var])  Calculates the T-test for the means of TWO INDEPENDENT samples of scores.
#ttest_rel(a, b[, axis]) Calculates the T-test on TWO RELATED samples of scores, a and b.
print a_list
print b_list
print stat.ttest_rel(a_list, b_list)