import os
import random
import sys
import glob 
import h5py
import keras
import IPython.display as ipd
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly 
import plotly.graph_objs as go
import plotly.offline as py
import plotly.tools as tls
import seaborn as sns
import scipy.io.wavfile
import tensorflow as tf

from tensorflow import keras
# from tensorflow.python.keras import backend as k
# from tensorflow.keras.models import Sequential
from keras import regularizers
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, EarlyStopping
from keras.callbacks import  History, ReduceLROnPlateau, CSVLogger

from keras.models import Sequential
from keras.models import Model

from keras.layers import Dense, Embedding, LSTM
from keras.layers import Input, Flatten, Dropout, Activation, BatchNormalization
from keras.layers import Conv1D, MaxPooling1D, AveragePooling1D
from keras import optimizers
from keras.optimizers import adam

from keras.preprocessing import sequence
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.utils import np_utils
from keras.utils import to_categorical
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedShuffleSplit
from scipy.fftpack import fft
from scipy import signal
from scipy.io import wavfile
from tqdm import tqdm
from tensorflow.keras import backend

input_duration=3

tmp1 = pd.read_pickle("./dummy.pkl")
tmp3 = pd.read_pickle("./dummy.pkl")
data3_df = pd.concat([tmp1, tmp3],ignore_index=True).reset_index(drop=True)


h5f = h5py.File('data.h5','r')
x_traincnn = h5f['one'][:]
x_testcnn = h5f['two'][:]
y_test = h5f['three'][:]
y_train = h5f['four'][:]
# lb = h5f['five'][:]
X_test = h5f['six'][:]
X_train = h5f['seven'][:]
# data3_df = h5f['last'][:]

h5f.close()


# model = tf.keras.models.load_model('model.h5')

# # use the keras predict function to run the model on our random file
# prediction = model.predict([train_X])
# # output the number in the emotions array the coresponds to the index of the prediction result. 
# print(categories[int(prediction[0][0])])
# print(prediction[0])




# # the model.json

# import json
# model_json = model.to_json()
# with open("model.json", "w") as json_file:
#     json_file.write(model_json)





# loading json and creating model
from keras.models import model_from_json
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)

# load weights into new model
loaded_model.load_weights("model/aug_noiseNshift_2class2_np.h5")
print("Loaded model from disk")
 
# evaluate loaded model on test data
opt = keras.optimizers.SGD(lr=0.0001, momentum=0.0, decay=0.0, nesterov=False)
loaded_model.compile(loss='categorical_crossentropy', optimizer='SGD', metrics=['accuracy'])
score = loaded_model.evaluate(x_testcnn, y_test, verbose=0)
print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1]*100))





print(len(data3_df))
data_test = pd.DataFrame(columns=['feature'])
for i in tqdm(range(len(data3_df))):
    X, sample_rate = librosa.load(data3_df.path[i], res_type='kaiser_fast',duration=input_duration,sr=22050*2,offset=0.5)
#     X = X[10000:90000]
    sample_rate = np.array(sample_rate)
    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=13), axis=0)
    feature = mfccs
    data_test.loc[i] = [feature]
test_valid = pd.DataFrame(data_test['feature'].values.tolist())
test_valid = np.array(test_valid)
test_valid_lb = np.array(data3_df.label)
lb = LabelEncoder()
test_valid_lb = np_utils.to_categorical(lb.fit_transform(test_valid_lb))
test_valid = np.expand_dims(test_valid, axis=2)




preds = loaded_model.predict(test_valid, 
                         batch_size=16, 
                         verbose=1)
print(preds)




preds1=preds.argmax(axis=1)
print(preds1)

abc = preds1.astype(int).flatten()
predictions = (lb.inverse_transform((abc)))
preddf = pd.DataFrame({'predictedvalues': predictions})
print(preddf[:10])


actual=test_valid_lb.argmax(axis=1)
abc123 = actual.astype(int).flatten()
actualvalues = (lb.inverse_transform((abc123)))


actualdf = pd.DataFrame({'actualvalues': actualvalues})
print(actualdf[:10])

finaldf = actualdf.join(preddf)

print(finaldf[20:40])


print(finaldf.groupby('actualvalues').count())

print(finaldf.groupby('predictedvalues').count())

print(finaldf.to_csv('Predictions.csv', index=False))

