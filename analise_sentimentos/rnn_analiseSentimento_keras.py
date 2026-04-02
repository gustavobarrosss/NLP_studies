import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Limpa avisos chatos do TensorFlow
import keras
from keras import layers
import numpy as np
import tensorflow as tf

#Definindo tamanho das frases
max_palavras = 10000 # 20k palavras mais frequentes
tamanho_sequencia = 800 #ler as primeiras 900 palavras de cada crítica

#carregando dataset nativo do Keras (IMDB)
(x_train, y_train), (x_val, y_val) = keras.datasets.imdb.load_data(num_words=max_palavras)

# precisamos uniformizar para o tamanho_sequencia (200)
x_train = keras.utils.pad_sequences(x_train, maxlen=tamanho_sequencia)
x_val = keras.utils.pad_sequences(x_val, maxlen=tamanho_sequencia)

#Arquitetura
model = keras.Sequential([
    #definindo o input como sendo os números do IMDB
    layers.Input(shape=(tamanho_sequencia,)), 

    # input_dim tem que ser igual ao max_palavras
    layers.Embedding(input_dim=max_palavras, output_dim=128),

    layers.SimpleRNN(units=64, dropout=0.2),

    layers.Dense(64, activation='relu'),
    #definindo função de ativação (sigmoid)

    layers.Dense(32, activation='tanh'),

    layers.Dense(1, activation='sigmoid')

])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

#trainando o modelo, definindo epochs, batch_size e distinguindo dados de treino e dados de teste
model.fit(x_train, y_train, epochs=5, batch_size=32, validation_data=(x_val, y_val))

model.summary()