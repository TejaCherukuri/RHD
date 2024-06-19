#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 14:45:19 2023

@author: Teja Cherukuri
"""

import cv2
import numpy as np
from aws.aws_utils import AWSUtils

def process_input(img_path, image_size):

    # Load image from S3
    img_obj = AWSUtils.load_file_from_s3(img_path)
    if img_obj is None:
        raise ValueError("Failed to load image from S3")

    # Read image with OpenCV
    img_bytes = img_obj.read()
    img_np = np.asarray(bytearray(img_bytes), dtype="uint8")
    image = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

    # Convert color and resize
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (image_size[0], image_size[1]), fx=1, fy=1, interpolation=cv2.INTER_CUBIC)
    image = np.expand_dims(image, axis=0)

    return image

def diabeticRetinopathyDiagnosis(img_path):
    
    image_size = (224, 224, 3)
    dr_label_mapper = { 0:'Normal', 1:'Mild DR', 2: 'Moderate DR', 3:'Sever DR', 4:'Proliferative DR'}

    s3_key = 'DR_Classifier.h5'
    dr_clf_model = AWSUtils.load_model_from_s3(s3_key)

    if dr_clf_model:
        # Model loaded successfully, proceed with predictions or further processing
        print("Model loaded successfully!")
    else:
        print("Failed to load model from S3. Check logs for details.")
    
    inp_img = process_input(img_path, image_size)
    pred_prob = dr_clf_model.predict(inp_img, verbose=0)
    pred_label = np.argmax(pred_prob, axis=-1)[0]
    dr_label = dr_label_mapper.get(pred_label)
    
    return dr_label