# -*- coding: utf-8 -*-
"""hmm_postagging.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JgVITeK0eAq5wH72tcBuenYBqn2w0R8b
"""

from google.colab import drive
drive.mount('/content/drive')
import numpy as np
!pip3 install conllu
import conllu
import nltk

transition_probs = nltk.FreqDist()
emission_probs = nltk.FreqDist()
count_dic={}
sent=[]
file="/content/drive/My Drive/en_atis-ud-train.conllu"
with open(file, "r", encoding="utf-8") as f:
                       data=f.read()
                       sentences = conllu.parse(data)
                       vocab1=[]
                       vocab2=[]
                       w1=[]
                       t1=[]
                       max_=0
                       for sentence in sentences:
                              sen=[]
                              words=[]
                              tags=[]
                              prev_tag=None
                              for token in sentence:
                                      w=token["form"]
                                      t=token["upos"]
                                      sen.append(w)
                                      if w not in vocab1:
                                         vocab1.append(w)
                                      if t not in vocab2:
                                         vocab2.append(t)
                                      w1.append(w)
                                      t1.append(t)
                                      if prev_tag is not None:
                                         transition_probs[(prev_tag, t)]+=1
                                      if t not in count_dic:
                                            count_dic[t]=1
                                      else:
                                         count_dic[t]+=1
                                      emission_probs[(t, w)] += 1
                                      prev_tag=t
                              sent.append(sen)
          
n_tags=len(vocab2)
n_words=len(vocab1)
tag_to_idx = {tag: i for i, tag in enumerate(vocab2)}
idx_to_tag = {i:tag for i, tag in enumerate(vocab2)}
word_to_idx = {word: i for i, word in enumerate(vocab1)}
ind_vocab2=[tag_to_idx[tag] for tag in vocab2]


alpha=0.001
for tag1 in vocab2:
    for tag2 in vocab2:
        key=(tag1,tag2)
        # print(key)
        count = transition_probs[key]
        # print(count)
        transition_probs[(tag1, tag2)] =  (count+alpha)/(count_dic[tag1]+alpha*n_tags)
        # print(transition_probs[(tag1, tag2)])

for tag in vocab2:
    for word in vocab1:
        count = emission_probs[(tag, word)]
        emission_probs[(tag, word)] = (count+alpha)/(count_dic[tag1]+alpha*n_words)


# transition_probs = nltk.LaplaceProbDist(transition_probs, bins=transition_probs.B() + 1)
# emission_probs=nltk.LaplaceProbDist(emission_probs, bins=emission_probs.B() + 1)
print(list(transition_probs.items())) 
# print(list(emission_probs))

##Baum-Welch algorithm
def forward_backward(observed_sequence):
    
    forward_probs = [[]]
    for tag in vocab2:
        forward_probs[0].append(emission_probs[(tag, observed_sequence[0])]/ n_tags)

    for t in range(1, len(observed_sequence)):
        forward_probs.append([])
        for tag1 in vocab2:
            ind=tag_to_idx[tag1]
            arr=[]
            for tag2 in vocab2:
               arr.append(forward_probs[t-1][ind] * transition_probs[(tag1,tag2)] * emission_probs[(tag2, observed_sequence[t])])
              #  print(forward_probs[t-1][ind])
              #  print(transition_probs[(tag1,tag2)])
              #  print(tag2,observed_sequence[t])
              #  print( emission_probs[(tag2, observed_sequence[t])])
            # print(arr)
            # print(sum(arr))
            forward_probs[t].append(sum(arr))
            # print(sum(arr))
    
    # print(forward_probs)
    backward_probs = [[] for _ in range(len(observed_sequence))]

    for tag in vocab2:
        backward_probs[-1].append(1)

    for t in range(len(observed_sequence)-2, -1, -1):
        for tag1 in vocab2:
            backward_probs[t].append(sum(backward_probs[t+1][ind] * transition_probs[(tag1, tag2)] * emission_probs[(tag2, observed_sequence[t+1])] for ind,tag2 in enumerate(vocab2)))

    forward=np.array(forward_probs)
    backward=np.array(backward_probs)
    xi=[np.zeros([n_tags,n_tags]) for _ in range(len(observed_sequence))]
    gamma=[np.zeros([n_tags]) for _ in range(len(observed_sequence))]

    for t in range(0, 1):
        sum_=0
        for i in range(0,n_tags):
          sum_+=forward[t][i]*backward[t][i]
        print(sum_)
        if sum_==0:
             p=10e-50
        else:
             p=sum_
    
    for t in range(0, len(observed_sequence)-1):
        for i in range(0,n_tags-1):
          t1=vocab2[i]
          for j in range(i+1,n_tags):
             t2=vocab2[j]
             xi[t][i][j]=((((forward[t][i]/p)* transition_probs[(t1,t2)])*emission_probs[(t2,observed_sequence[t+1])])*backward[t+1][j])
             xi[t][j][i]=((((forward[t][j]/p)* transition_probs[(t2,t1)])*emission_probs[(t1,observed_sequence[t+1])])*backward[t+1][i])

    xi=np.array(xi)
    
    for t in range(0, len(observed_sequence)-1):
       for i in range(0,n_tags):
                gamma[t][i]=forward[t][i]*backward[t][i]
              
    return xi,gamma

print(transition_probs.items())

pi=np.zeros(n_tags)
for n in range(1):
      xisum=np.zeros(n_tags)
      sum_gamma=np.zeros(n_tags)
      xi_tot=np.zeros((n_tags,n_tags))
      gamma_tot=np.zeros((n_tags,n_words))
      
      for observed_sequence in sent:
            print(observed_sequence)

            xi,gamma=forward_backward(observed_sequence)
          
            
            #updating transition probabilities
            for i in range(0,n_tags-1):
                      t1=vocab2[i]
                      for j in range(i+1,n_tags):
                        t2=vocab2[j]
                        sum1=0
                        sum2=0
                        for t in range(0, len(observed_sequence)-1):
                          sum1+=xi[t][i][j]
                          sum2+=xi[t][j][i]
                        # transition_probs[(t1,t2)]=sum_
                        xi_tot[i][j]+=sum1
                        xisum[i]+=sum1
                        xi_tot[j][i]+=sum2
                        xisum[j]+=sum2

            for i in range(0,n_tags):
               pi[i]+=gamma[0][i]
               for t in range(0, len(observed_sequence)-1):
                        sum_gamma[i]+=gamma[t][i]

            for i in range(0,n_tags):
                for word in vocab1:
                  j=word_to_idx[word]
                  sum1=0
                  for t in range(0, len(observed_sequence)-1):
                        if word==observed_sequence[t]:
                          sum1+=gamma[t][i]
                  gamma_tot[i][j]+=sum1
                  # emission_probs[(vocab2[i],word)]=sum1
      for i in range(0,n_tags-1):
              t1=vocab2[i]
              for j in range(i+1,n_tags):
                t2=vocab2[j]
                transition_probs[(t1,t2)]=xi_tot[i][j]/xisum[i]
                transition_probs[(t2,t1)]=xi_tot[j][i]/xisum[j]
      for i in range(0,n_tags):
              t=vocab2[i]
              pi[i]/=len(sent)
              for j in range(0,n_words):
                 word=vocab1[j]
                 emission_probs[(t,word)]=gamma_tot[i][j]/sum_gamma[i]

print(transition_probs.items())
print(emission_probs.items())

def viterbi(observed_sequence):
        V = [[]]
        path={}
        for tag in vocab2:
                i=tag_to_idx[tag]
                V[0].append(pi[i]*emission_probs[(tag, observed_sequence[0])])
                ind=tag_to_idx[tag]
                path[ind]=[tag]
        T=len(observed_sequence)
        for t in range(1, T):
                
                V.append([])
                new_path={}
                for tag1 in vocab2:
                    array=[ V[t-1][tag_to_idx[tag2]] *transition_probs[(tag2,tag1)]*emission_probs[(tag1, observed_sequence[t])] for tag2 in vocab2]
                    
                    prob=max(array)
                    index = array.index(prob)
                    # print(vocab2[index])
                    V[t].append(prob)
                    ind=tag_to_idx[tag1]
                    new_path[ind]=path[index]+[tag1]
                path=new_path
                # print(path)
        array= [V[t-1][tag_to_idx[tag2]] *transition_probs[(tag2,tag1)]*emission_probs[(tag1, observed_sequence[t])] for tag2 in vocab2]   
        prob=max(array)
        index = array.index(prob)
        best_path=path[index]
        return best_path

obs_seq="i need information for ground transportation denver colorado".split()
print(obs_seq)
print(viterbi(obs_seq))
obs_seq=['show', 'me', 'the', 'flights', 'from', 'cleveland', 'to', 'memphis']
obs_seq2=['please', 'show', 'me', 'the', 'flights', 'from', 'atlanta', 'to', 'denver']
print(obs_seq)
print(viterbi(obs_seq))
print(obs_seq2)
print(viterbi(obs_seq2))
obs_seq4="what kind of aircraft does delta fly before 8 am on august second from boston to denver".split()
print(obs_seq4)
print(viterbi(obs_seq4))

# pi,transition_probs,emission_probs