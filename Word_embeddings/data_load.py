import json
count=0
with open("reviews_Movies_and_TV.json","r") as f:
           with open("input2.txt","w") as f2:
                    for line in f:
                        if count<7000:
                           count+=1
                           f2.write((json.loads(line))['reviewText'])
                        else:
                           break
           
   