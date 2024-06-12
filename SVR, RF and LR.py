#!/usr/bin/env python
# coding: utf-8

# # SVR, RF and LR

# In[357]:


import numpy as np
import os
import pandas as pd
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV
from PyALE import ale
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from sklearn.inspection import permutation_importance
from sklearn.ensemble import RandomForestRegressor


# ## Support Vector Regression

# In[ ]:


#Independent variables X and dependent variable y
X = 
y = 

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)


# In[383]:


# Standardize the features (important for SVR)

def scaler(x):
    y = x.copy()
    for i in range(0,len(y)):
        y[i] = (y[i]-np.mean(y))/np.std(y)
    return y

def inverse_scaler(x, mean, sd):
    y = x.copy()
    for i in range(0,len(y)):
        y[i] = sd*y[i]+mean
    return y

def scale_Xy(X, y):
    y_scaled = scaler(y)
    X_scaled=X.copy(deep=True)
    for column in X_scaled:
        X_scaled[column] = (X_scaled[column] - X_scaled[column].mean()) / X_scaled[column].std() 
    return X_scaled, y_scaled

X_train_scaled, y_train_scaled = scale_Xy(X_train, y_train)
X_test_scaled, y_test_scaled = scale_Xy(X_test, y_test)


# In[384]:


# Define the SVR model
svr = SVR()

# Define the parameter grid to search
param_grid = {
    'kernel': ['linear', 'poly', 'rbf'],
    'C': [0.1, 1, 10],
    'epsilon': [0.01, 0.1, 0.2]
}

# Create the GridSearchCV object
grid_search_svr = GridSearchCV(estimator=svr, param_grid=param_grid, scoring='neg_mean_squared_error', cv=5)

# Fit the grid search to the data
grid_search_svr.fit(X_train_scaled, y_train_scaled)

# Print the best parameters and corresponding score
print("Best Parameters:", grid_search_svr.best_params_)
print("Best Negative Mean Squared Error:", grid_search_svr.best_score_)

# Get the best model
best_svr = grid_search_svr.best_estimator_


# In[385]:


#Evaluate the best model on the test set
y_pred_scaled = best_svr.predict(X_test_scaled)
y_pred = inverse_scaler(y_pred_scaled, np.mean(y_test), np.std(y_test))

mse_scaled = mean_squared_error(y_test_scaled, y_pred_scaled)
print(f'Mean Squared Error on Test Set Scaled: {mse_scaled}')

mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error on Test Set: {mse}')


# ## Random Forests

# In[ ]:


#Define the Random Forest model
rf = RandomForestRegressor()

# Define the parameter grid to search
param_grid_rf = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

#Create the GridSearchCV object
grid_search_rf = GridSearchCV(estimator=rf, param_grid=param_grid_rf, scoring='neg_mean_squared_error', cv=5)

#Fit the grid search to the data
grid_search_rf.fit(X_train_scaled, y_train_scaled)

#Print the best parameters and corresponding score
print("Best Parameters:", grid_search_rf.best_params_)
print("Best Negative Mean Squared Error:", grid_search_rf.best_score_)

#Get the best model
best_rf = grid_search_rf.best_estimator_


# In[398]:


#Evaluate the best model on the test set
y_pred_rf = best_rf.predict(X_test_scaled)

mse_rf = mean_squared_error(y_test_scaled, y_pred_rf)
print(f'Mean Squared Error on Test Set: {mse_rf}')


# ## Global interpretation methods

# In[396]:


#Obtain the permuted feature importances of all features
r = permutation_importance(best_svr, X_test_scaled, y_test_scaled, n_repeats=10, random_state=0, scoring='neg_mean_squared_error')
r.importances_mean


# In[ ]:


#Plot the feature importance plot
feature_importance = pd.DataFrame({'Feature': X.columns, 'Importance': r.importances_mean})
feature_importance = feature_importance.sort_values('Importance', ascending=True)
feature_importance.plot(x='Feature', y='Importance', kind='barh', figsize=(10, 6))


# In[ ]:


#Obtain the ALE plots for the 4 most important features
ale_eff = ale(X=X_test, model=best_rf, feature=[""], grid_size=50, include_CI=False)


# ## Logistic regression

# In[382]:


# X contains predictors and y is the target variable

y = 
X = 

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Create and fit the Logistic Regression model
lr = LogisticRegression(penalty='elasticnet', solver='saga',l1_ratio=0.5)  # Adjust alpha and l1_ratio as needed
lr.fit(X_train_scaled, y_train)

# Make predictions on the test set
predictions = lr.predict(X_test_scaled)


# In[ ]:


#Create confusion matrix for our logistic regression model
cm = confusion_matrix(y_test, predictions, labels=[0, 1])
disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                               display_labels=[0,1])
disp.plot()
plt.show()


# In[ ]:


#Obtain feature importance plot

coefficients = lr.coef_[0]

feature_importance = pd.DataFrame({'Feature': X.columns, 'Importance': np.abs(coefficients)})
feature_importance = feature_importance.sort_values('Importance', ascending=True)
feature_importance.plot(x='Feature', y='Importance', kind='barh', figsize=(10, 6))

