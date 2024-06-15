#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 14:45:19 2023

@author: Teja Cherukuri
"""

import cv2
import numpy as np

from tensorflow.keras.models import load_model


def process_input(img_path, image_size):
    image = cv2.imread(img_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (image_size[0],image_size[1]), fx=1, fy=1,interpolation = cv2.INTER_CUBIC)
    image = np.expand_dims(image, axis=0)

    return image

def diabeticRetinopathyDiagnosis(img_path):
    
    image_size = (224, 224, 3)
    dr_label_mapper = { 0:'Normal', 1:'Mild DR', 2: 'Moderate DR', 3:'Sever DR', 4:'Proliferative DR'}
    
    dr_clf_config = 'Diabetic Retinopathy/dr_classifier.h5'
    dr_clf_model = load_model(dr_clf_config)
    
    inp_img = process_input(img_path, image_size)
    pred_prob = dr_clf_model.predict(inp_img, verbose=0)
    pred_label = np.argmax(pred_prob, axis=-1)[0]
    dr_label = dr_label_mapper.get(pred_label)
    
    return dr_label