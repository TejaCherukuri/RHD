#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 17:51:37 2023

@author: Teja Cherukuri
"""
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.cm as cm
from PIL import Image


def get_img_array(img_path, size):
    img = keras.preprocessing.image.load_img(img_path, target_size=size)
    array = keras.preprocessing.image.img_to_array(img)
    array = np.expand_dims(array, axis=0)
    return array


def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    grad_model = tf.keras.models.Model(
        [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
    )

    # Then, we compute the gradient of the top predicted class for our input image
    # with respect to the activations of the last conv layer
    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    # This is the gradient of the output neuron (top predicted or chosen)
    # with regard to the output feature map of the last conv layer
    grads = tape.gradient(class_channel, last_conv_layer_output)

    # This is a vector where each entry is the mean intensity of the gradient
    # over a specific feature map channel
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # We multiply each channel in the feature map array
    # by "how important this channel is" with regard to the top predicted class
    # then sum all the channels to obtain the heatmap class activation
    last_conv_layer_output = last_conv_layer_output[0]
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # For visualization purpose, we will also normalize the heatmap between 0 & 1
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    return heatmap.numpy()


def apply_grad_cam(img_path, img, img_size):
    model_builder = keras.applications.vgg16.VGG16
    preprocess_input = keras.applications.vgg16.preprocess_input
    last_conv_layer_name = "block4_pool"
    
    # Prepare image
    img_array = preprocess_input(preprocess_input(get_img_array(img_path, size=img_size)))

    # Make model
    model = model_builder(weights="imagenet")

    # Remove last layer's softmax
    model.layers[-1].activation = None

    # Generate class activation heatmap
    heatmap = make_gradcam_heatmap(img_array, model, last_conv_layer_name)
    
    # Load the original image
    #img = keras.preprocessing.image.load_img(img_path)
    #img = keras.preprocessing.image.img_to_array(img)

    # We rescale heatmap to a range 0-255
    heatmap = np.uint8(255 * heatmap)

    # We use jet colormap to colorize heatmap
    jet = cm.get_cmap("jet")

    # We use RGB values of the colormap
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]

    # We create an image with RGB colorized heatmap
    jet_heatmap = keras.preprocessing.image.array_to_img(jet_heatmap)
    jet_heatmap = jet_heatmap.resize((img.shape[1], img.shape[0]))
    jet_heatmap = keras.preprocessing.image.img_to_array(jet_heatmap)

    # Superimpose the heatmap on original image
    superimposed_img = jet_heatmap * 0.4 + img #alpha = 0.4
    superimposed_img = keras.preprocessing.image.array_to_img(superimposed_img)

    return superimposed_img
    
def apply_clahe(img_path, file_name):
    
    # Reading the image from the present directory
    image = cv2.imread(img_path)
    
    img_size = (224, 224)
    
    # Resizing the image for compatibility
    image = cv2.resize(image, img_size)
    
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    rgb_planes = list(cv2.split(rgb))
    clahe = cv2.createCLAHE(clipLimit=5.0)
    rgb_planes[0] = clahe.apply(rgb_planes[0])
    rgb_planes[1] = clahe.apply(rgb_planes[1])
    rgb_planes[2] = clahe.apply(rgb_planes[2])
    rgb_clahe = cv2.merge(rgb_planes)
    
    # Save CLAHE Image
    clahe_path = "static/ProcessedImgs/CLAHE/"+file_name+".png"
    img_clahe = Image.fromarray(rgb_clahe, "RGB")
    img_clahe.save(clahe_path)
    
    img = np.array(rgb_clahe)
    img = apply_grad_cam(img_path, img, img_size)
    
    # Save GradCAM Image
    gradcam_path = "static/ProcessedImgs/GradCAM/"+file_name+".png"
    img.save(gradcam_path)
    
