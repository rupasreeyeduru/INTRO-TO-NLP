Run $python3 data_load.py to load data into input.txt from json file
To run svd model:
   $python3 svd.py
Required to change train=1 to train and train=0 to load the model without starting to train
To run cbow model:
   $python3 cbow.py
Required to  change Train=1 to train and train=0 to load the model without starting to train


models:
(Required to place in same folder as .py files)
svd_matrix.npz contains embedding vectors obatined by first model(
cbow_matrix.npz contains embedding vectors obtained by cbow-negative sampling model    

Models location:
https://drive.google.com/drive/folders/1ipQceO6O5oCMbtoa9tnuQNBmovCejFRl?usp=share_link