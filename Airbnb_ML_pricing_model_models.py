#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: valentinakomarova
"""

import csv
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn import model_selection
from sklearn.metrics import mean_absolute_error
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score

df = pd.read_csv('clean_Airbnb_data.csv')
df.head()
