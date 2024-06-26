#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Teja Cherukuri
"""
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.cm as cm
from PIL import Image
from aws.aws_utils import AWSUtils
from io import BytesIO

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


def apply_grad_cam(img_key, img_size, filename):
    try:
        model_builder = keras.applications.vgg16.VGG16
        preprocess_input = keras.applications.vgg16.preprocess_input
        last_conv_layer_name = "block4_pool"
        
        # Load image from S3
        img_path = AWSUtils.load_file_from_s3(img_key)
        
        # Read and preprocess image for GradCAM
        img_array = keras.preprocessing.image.img_to_array(keras.preprocessing.image.load_img(img_path, target_size=img_size))
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        
        # Make model
        model = model_builder(weights="imagenet")
        model.layers[-1].activation = None
        
        # Generate class activation heatmap
        heatmap = make_gradcam_heatmap(img_array, model, last_conv_layer_name)
        
        # We rescale heatmap to a range 0-255
        heatmap = np.uint8(255 * heatmap)
        
        # We use jet colormap to colorize heatmap
        jet = cm.get_cmap("jet")
        
        # We use RGB values of the colormap
        jet_colors = jet(np.arange(256))[:, :3]
        jet_heatmap = jet_colors[heatmap]
        
        # Create RGB heatmap image
        jet_heatmap = keras.preprocessing.image.array_to_img(jet_heatmap)
        jet_heatmap = jet_heatmap.resize((img_array.shape[2], img_array.shape[1]))
        jet_heatmap = keras.preprocessing.image.img_to_array(jet_heatmap)
        
        # Superimpose the heatmap on original image
        superimposed_img = (jet_heatmap * 0.4 + img_array[0] / 2).astype(np.uint8)
        superimposed_img = keras.preprocessing.image.array_to_img(superimposed_img)
        
        # Save GradCAM Image to BytesIO object
        gradcam_img_bytes = BytesIO()
        superimposed_img.save(gradcam_img_bytes, format='PNG')
        gradcam_img_bytes.seek(0)
        
        # Upload GradCAM Image to S3 using upload_image_to_s3 method
        gradcam_key = f"static/processed_imgs/GradCAM/{filename}.png"
        success = AWSUtils.upload_file_to_s3(gradcam_img_bytes, gradcam_key)
        
        if success:
            print("GradCAM image uploaded to S3")
            return True, gradcam_key
        else:
            return False, None
        
    except Exception as e:
        print(f"Error processing image with GradCAM: {e}")
        return False, None
    

def apply_clahe(img_key, name, image_name):

    filename = name + '_' + image_name

    try:
        # Load image from S3
        img_path = AWSUtils.load_file_from_s3(img_key)

        # Read image with OpenCV
        img_np = np.asarray(bytearray(img_path.read()), dtype="uint8")
        image = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        
        # Process image with CLAHE
        img_size = (224, 224)
        image = cv2.resize(image, img_size)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb_planes = list(cv2.split(rgb))
        clahe = cv2.createCLAHE(clipLimit=5.0)
        rgb_planes[0] = clahe.apply(rgb_planes[0])
        rgb_planes[1] = clahe.apply(rgb_planes[1])
        rgb_planes[2] = clahe.apply(rgb_planes[2])
        rgb_clahe = cv2.merge(rgb_planes)
        
        # Convert processed image back to PIL format for saving
        img_clahe = Image.fromarray(rgb_clahe, "RGB")
        
        # Save CLAHE Image to BytesIO object
        clahe_img_bytes = BytesIO()
        img_clahe.save(clahe_img_bytes, format='PNG')
        clahe_img_bytes.seek(0)
        
        # Upload CLAHE Image to S3 using upload_image_to_s3 method
        clahe_key = f"static/processed_imgs/CLAHE/{filename}.png"
        success = AWSUtils.upload_file_to_s3(clahe_img_bytes, clahe_key)
        
        if success:
            # Apply GradCAM to the processed image
            print("CLAHE image uploaded to S3")
            apply_grad_cam(clahe_key, img_size, filename)
            return True, clahe_key
        else:
            return False, None
        
    except Exception as e:
        print(f"Error processing image with CLAHE: {e}")
        return False, None