#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 11:09:29 2023

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

def digitalEyeCateractDiagnosis(img_path):
    
    ext_eye_image_size = (156,156,3)
    cataract_label_mapper = { 0:'Cataract', 1:'Normal'}
    ext_eye_cataract_clf_config = 'Cataract/external-eyes_cataract_classsifier.h5'
    ext_eye_cataract_clf_model = load_model(ext_eye_cataract_clf_config)
    
    inp_img = process_input(img_path, ext_eye_image_size)
    pred_prob = ext_eye_cataract_clf_model.predict(inp_img, verbose=0)
    pred_label = np.argmax(pred_prob, axis=-1)[0]
    ext_eye_cataract_label = cataract_label_mapper.get(pred_label)
    
    return ext_eye_cataract_label

def retinalScanCateractDiagnosis(img_path):
    
    fundus_image_size = (224,224,3)
    fundus_img_cataract_label_mapper = { 0:'Cataract', 1:'Normal'}
    fundus_img_cataract_clf_config = 'Cataract/fundus-image_cataract_classifier.h5'
    fundus_img_cataract_clf_model = load_model(fundus_img_cataract_clf_config)
    
    inp_img = process_input(img_path, fundus_image_size)
    pred_prob = fundus_img_cataract_clf_model.predict(inp_img, verbose=0)
    pred_label = np.argmax(pred_prob, axis=-1)[0]
    fundus_img_cataract_label = fundus_img_cataract_label_mapper.get(pred_label)
    
    return fundus_img_cataract_label