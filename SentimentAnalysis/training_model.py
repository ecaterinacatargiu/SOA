import pandas as pd
import datetime
import pickle
import os

from tensorflow.keras.layers import Input, Conv1D, MaxPooling1D, Dense, GlobalMaxPooling1D, Embedding
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import Model

from sklearn.model_selection import train_test_split

df = pd.read_csv('./dataset/training.1600000.processed.noemoticon.csv', encoding='ISO-8859-1', header=None)
df.drop([1, 2, 3, 4], axis=1, inplace=True)
df.columns = ['sentiment', 'data']
y = df['sentiment']

df_train, df_test, y_train, y_test = train_test_split(df['data'], y, test_size=0.33, random_state=42)

max_words = 10000
tokenizer = Tokenizer(max_words)
tokenizer.fit_on_texts(df_train)
sequence_train = tokenizer.texts_to_sequences(df_train)
sequence_test = tokenizer.texts_to_sequences(df_test)
word2vec = tokenizer.word_index
V = len(word2vec)

data_train = pad_sequences(sequence_train)
T = data_train.shape[1]
data_test = pad_sequences(sequence_test, maxlen=T)

D = 20
i = Input((T,))
x = Embedding(V + 1, D)(i)
x = Conv1D(32, 3, activation='relu')(x)
x = MaxPooling1D(3)(x)
x = Conv1D(64, 3, activation='relu')(x)
x = MaxPooling1D(3)(x)
x = Conv1D(128, 3, activation='relu')(x)
x = GlobalMaxPooling1D()(x)
x = Dense(6, activation='softmax')(x)

model = Model(i, x)
model.summary()
model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

cnn_senti = model.fit(data_train, y_train, validation_data=(data_test, y_test), epochs=5, batch_size=252)

datetime_now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

os.mkdir("./models/{}".format(datetime_now))

model.save(r"./models/{}/model.tfsm".format(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")))

with open(r'./models/{}/data_shape.txt'.format(datetime_now), "w") as handle:
    handle.write(str(T))

with open(r'./models/{}/tokenizer.pickle'.format(datetime_now), 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
