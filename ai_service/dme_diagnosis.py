#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 22:20:52 2023

@author : Teja Cherukuri
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

def dme_Diagnosis(img_path):
    
    image_size = (224,224,3)
    dme_label_mapper = { 0:'No Referable DME', 1:'Referable DME'}
    dme_clf_config = 'Diabetic Macular Edema/dme_classifier.h5'
    dme_clf_model = load_model(dme_clf_config)
    
    inp_img = process_input(img_path, image_size)
    pred_prob = dme_clf_model.predict(inp_img, verbose=0)
    pred_label = np.argmax(pred_prob, axis=-1)[0]
    dme_label = dme_label_mapper.get(pred_label)
    
    return dme_label