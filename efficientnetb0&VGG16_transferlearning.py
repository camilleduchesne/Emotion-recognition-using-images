# -*- coding: utf-8 -*-
"""EfficientNetB0_transferLearning.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Jmc71j5HZurv0A8jsVnKTidUbkxKic6C
"""

import pandas as pd
import tensorflow as tf
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
#import sklearn
import matplotlib.pyplot as plt
import copy
from torchvision import transforms
from keras.models import Sequential, save
from keras.layers import Dense, Conv2D, Flatten, BatchNormalization, MaxPool2D, Dropout, Softmax, ReLU
IMG_SIZE = 224

#NB default value for dropout rate is 0.2
from tensorflow.keras.applications import EfficientNetB0 
model = EfficientNetB0(include_top=False,weights='imagenet')

dir = '/content/drive/Othercomputers/Mon MacBook Pro/Documents/labelled_folder'

batch_size = 32

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    directory = dir,
    labels='inferred',
    batch_size = batch_size,
    image_size=(IMG_SIZE, IMG_SIZE),
    shuffle = True,
    validation_split = 0.3,
    subset = 'training',
    seed = 123,
    label_mode='categorical')

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    directory = dir,
    labels='inferred',
    batch_size = batch_size,
    image_size=(IMG_SIZE, IMG_SIZE),
    shuffle = True,
    validation_split = 0.3,
    subset = 'validation',
    seed = 123,
    label_mode='categorical')

#Proceed with Data augmentation 
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers

img_augmentation = Sequential(
    [
        layers.RandomRotation(factor=0.15),
        layers.RandomTranslation(height_factor=0.1, width_factor=0.1),
        layers.RandomFlip(),
        layers.RandomContrast(factor=0.1),
    ],
    name="img_augmentation",
)

import os
strategy = tf.distribute.MirroredStrategy()

# Set random seed and set device to GPU
#torch.manual_seed(1234)
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

from tensorflow.keras.applications import EfficientNetB0

with strategy.scope():
    inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = img_augmentation(inputs)
    outputs = EfficientNetB0(include_top=True, weights=None, classes=7)(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

model.summary()

epochs = 5 #before this was set to 40
hist = model.fit(train_ds, epochs=epochs, validation_data=val_ds, verbose=2)

import matplotlib.pyplot as plt

def plot_hist(hist):
    plt.plot(hist.history["accuracy"])
    plt.plot(hist.history["val_accuracy"])
    plt.title("model accuracy")
    plt.ylabel("accuracy")
    plt.xlabel("epoch")
    plt.legend(["train", "validation"], loc="upper left")
    plt.show()


plot_hist(hist)
#we can see in the plot that we have convergence between the training and validation accuracy (arround 75%)

def build_model(num_classes):
    inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = img_augmentation(inputs)
    model = EfficientNetB0(include_top=False, input_tensor=x, weights="imagenet")

    # Freeze the pretrained weights
    model.trainable = False

    # Rebuild top
    x = layers.GlobalAveragePooling2D(name="avg_pool")(model.output)
    x = layers.BatchNormalization()(x)

    top_dropout_rate = 0.2
    x = layers.Dropout(top_dropout_rate, name="top_dropout")(x)
    outputs = layers.Dense(7, activation="softmax", name="pred")(x) #take input the number of classes (here 7)

    # Compile
    model = tf.keras.Model(inputs, outputs, name="EfficientNet")
    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-2)
    model.compile(
        optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"]
    )
    return model

with strategy.scope():
    model = build_model(num_classes=7)

epochs = 50
hist = model.fit(train_ds, epochs=epochs, validation_data=val_ds, verbose=2)

import matplotlib.pyplot as plt

def plot_hist(hist):
    plt.plot(hist.history["accuracy"])
    plt.plot(hist.history["val_accuracy"])
    plt.title("model accuracy")
    plt.ylabel("accuracy")
    plt.xlabel("epoch")
    plt.legend(["train", "validation"], loc="upper left")
    plt.show()


plot_hist(hist)

def unfreeze_model(model):
    # We unfreeze the top 20 layers while leaving BatchNorm layers frozen
    for layer in model.layers[-20:]:
        if not isinstance(layer, layers.BatchNormalization):
            layer.trainable = True

    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
    model.compile(
        optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"]
    )


unfreeze_model(model)

epochs = 50
hist = model.fit(train_ds, epochs=epochs, validation_data=val_ds, verbose=2)
plot_hist(hist)

def unfreeze_model(model):
    # We unfreeze the top 20 layers while leaving BatchNorm layers frozen
    for layer in model.layers[-20:]:
        if not isinstance(layer, layers.BatchNormalization):
            layer.trainable = True

    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-5)
    model.compile(
        optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"]
    )


unfreeze_model(model)

epochs = 50
hist = model.fit(train_ds, epochs=epochs, validation_data=val_ds, verbose=2)
plot_hist(hist)

"""##VGG16"""

from keras.applications.vgg16 import VGG16
model = VGG16()
print(model.summary())

from keras.applications.vgg16 import VGG16

with strategy.scope():
    inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = img_augmentation(inputs)
    outputs = VGG16(include_top=True, weights=None, classes=7)(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )

model.summary()

epochs = 40
hist = model.fit(train_ds, epochs=epochs, validation_data=val_ds, verbose=2)

def build_model(num_classes):
    inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = img_augmentation(inputs)
    model = VGG16(include_top=False, input_tensor=x, weights="imagenet")

    # Freeze the pretrained weights
    model.trainable = False

    # Rebuild top
    x = layers.GlobalAveragePooling2D(name="avg_pool")(model.output)
    x = layers.BatchNormalization()(x)

    top_dropout_rate = 0.2
    x = layers.Dropout(top_dropout_rate, name="top_dropout")(x)
    outputs = layers.Dense(7, activation="softmax", name="pred")(x) #take input the number of classes (here 7)

    # Compile
    model = tf.keras.Model(inputs, outputs, name="VGG16")
    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-2)
    model.compile(
        optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"]
    )
    return model

with strategy.scope():
    model = build_model(num_classes=7)

epochs = 25
hist = model.fit(train_ds, epochs=epochs, validation_data=val_ds, verbose=2)
plot_hist(hist)

def unfreeze_model(model):
    # We unfreeze the top 20 layers while leaving BatchNorm layers frozen
    for layer in model.layers[-20:]:
        if not isinstance(layer, layers.BatchNormalization):
            layer.trainable = True

    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
    model.compile(
        optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy"]
    )


unfreeze_model(model)

epochs = 40
hist = model.fit(train_ds, epochs=epochs, validation_data=val_ds, verbose=2)
plot_hist(hist)