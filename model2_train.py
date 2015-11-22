import pickle
import numpy as np
from collections import Counter
from copy import deepcopy
import re
import pdb
import matplotlib.pyplot as plt
import numpy.random as nrand
import model2_helpers as hp

print('*************** Training IBM Model 1 ***************')
totalSteps = 10
eng_dict = pickle.load(open("../englishDict10.dict",'r'))
french_dict = pickle.load(open("../frenchDict10.dict",'r'))
eng_sent = [];
french_sent = [];

lengthsFr = [];
lengthsEn = [];

with open("../CleanedFrench10.txt", "r") as fp:
	for x in fp:
	    xTemp = re.sub('[\n]', '', x)
            words = xTemp.split()
            french_sent.append(words)
            lengthsFr.append(len(words))

with open("../CleanedEnglish10.txt", "r") as fp:
	for x in fp:
	    xTemp = re.sub('[\n]', '', x)
            words = xTemp.split()
            eng_sent.append(words)
            lengthsEn.append(len(words))
    
#count_matrix = np.zeros((len(eng_dict),len(french_dict)))*(1.0/(len(eng_dict)*len(french_dict)));

translation_matrix = np.ones((len(eng_dict),len(french_dict)))*(1.0/(len(eng_dict)*len(french_dict)));
alignment_matrix = {}

for i in range(8):
    for j in range(8):

        if i < 7 and j < 7:
            alignment_matrix[(j,i)] = np.ones(((i+1)*5,(j+1)*5))*0.01
        elif i < 7 and j == 7:
            alignment_matrix[(j,i)] = np.ones(((i+1)*5,50))*0.01
        elif i == 7 and j < 7:
            alignment_matrix[(j,i)] = np.ones((50, (i+1)*5))*0.01
        else:
            alignment_matrix[(j,i)] = np.ones((50,50))*0.01
            
lambda_norm = np.zeros((len(eng_dict)))
count_matrix = np.zeros((len(eng_dict),len(french_dict)))

#plt.plot(lengthsEn, lengthsFr, 'ro')
fit = np.polyfit(lengthsEn, lengthsFr, 1)
lengthsPred = []
for i in lengthsEn:
    lengthsPred.append(int(np.random.normal(i*fit[0],5)))

#plt.plot(lengthsEn, lengthsPred, 'g.')
#plt.show()

with open('../FitParams10.txt', 'wb') as fp:
    fp.write(str(fit[0]))
    fp.write('\n')
    fp.write('5')

print(' =====> Obtained the length distribution')

for step in range(totalSteps):

    print '=====> Iteration %d started'%(step)	
    
    # Updating count_matrix 

    for i in range(len(eng_sent)):
        #pdb.set_trace()
        eng_words = eng_sent[i]
        french_words = french_sent[i]

        for e in eng_words:
            for f in french_words:
                count_matrix[eng_dict[e]][french_dict[f]] += hp.c_of_f_given_e(e, f, eng_words, french_words, eng_dict, french_dict, alignment_matrix, translation_matrix)

    # Updating translation_matrix

    for englishWord in eng_dict:
        
        temp = 0
        for frenchWord in french_dict:
            temp += count_matrix[eng_dict[englishWord]][french_dict[frenchWord]]
    
        lambda_norm[eng_dict[englishWord]] = temp
        for frenchWord in french_dict:	
            translation_matrix[eng_dict[englishWord]][french_dict[frenchWord]] = (count_matrix[eng_dict[englishWord]][french_dict[frenchWord]])/temp
    
    # Computing the mu_matrix

    mu_matrix = hp.createMuMatrix()
    
    for s in range(len(eng_sent)):
        m_temp = len(french_sent[s])
        l_temp = len(eng_sent[s])
        
        for j in range(m_temp):
            mu_temp = 0
            for i in range(l_temp):
               mu_temp  += hp.c_of_i_given_jmlFE(i, j, m_temp, l_temp, eng_sent[s], french_sent[s], translation_matrix, alignment_matrix, eng_dict, french_dict)
            mu_matrix[hp.alignmentMapping(m_temp, l_temp)][j] += mu_temp

    
    # Updating alignment_matrix
    
    alignment_temp = hp.createAlignmentMatrix()
    for s in range(len(eng_sent)):
        m_temp = len(french_sent[s])
        l_temp = len(eng_sent[s])

        for i in range(l_temp):
            for j in range(m_temp):
                alignment_temp[hp.alignmentMapping(m_temp, l_temp)][i][j] += hp.c_of_i_given_jmlFE(i, j, m_temp, l_temp, eng_sent[s], french_sent[s], translation_matrix, alignment_matrix, eng_dict, french_dict)/mu_matrix[hp.alignmentMapping(m_temp, l_temp)][j]

    alignment_matrix = alignment_temp
    with open("../translationMatrix10.txt", "w") as fp:
        for i in range(len(translation_matrix)):
            for j in range(len(translation_matrix[i])):
                print >> fp, translation_matrix[i][j],
            print >> fp


print('=====> Finished training, saving data')
print('=====> Saved data. Have a nice day!')
