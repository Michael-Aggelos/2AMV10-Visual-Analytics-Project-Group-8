#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
import math


# In[36]:


# Incorporate data
df_og = pd.read_csv('C:\\Users\\nidhi\\Documents\\Team stats complete incl offrts.csv')
df = df_og.copy(deep=True)
df = df.dropna().reset_index().drop(['index', 'Unnamed: 0'], axis=1)


# In[37]:


#Input goes here (I put 2003 as start and 2016 as end as an example)
input_1 = 2003
input_2 = 2016
seasons_selected = []

for i in range(input_1,input_2):
    p1 = str(i)[2:4]
    p2 = str(i+1)[2:4]
    seasons_selected.append(f'20{p1}-{p2}')

df_subset = df[df['SEASON_2'].isin(seasons_selected)].reset_index().drop(['index'],axis=1)


# ## Random forest model

# In[136]:


#Encode the data
encoded_data = pd.get_dummies(df_subset, columns = ['SEASON_2'])

#Independent variables X and dependent variable y
X = encoded_data.drop(['TEAM_NAME', 'Offensive rating'], axis=1)
y = encoded_data['Offensive rating']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)


# In[137]:


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
grid_search_rf.fit(X_train, y_train)

#Print the best parameters and corresponding score
print("Best Parameters:", grid_search_rf.best_params_)
print("Best Negative Mean Squared Error:", grid_search_rf.best_score_)

#Get the best model
best_rf = grid_search_rf.best_estimator_


# In[142]:


#Evaluate the best model on the test set
y_pred_rf = best_rf.predict(X_test)

mse_rf = mean_squared_error(y_test, y_pred_rf)
#print(f'Mean Squared Error on Test Set: {mse_rf}')


# In[170]:


plt.figure(figsize=(10,6))
plt.plot(y_pred_rf, color='r', linewidth=0.5)
plt.plot(y_test.reset_index()['Offensive rating'], color='b', linewidth=0.5)
plt.show()


# In[156]:


#Obtain the permuted feature importances of all features
r = permutation_importance(best_rf, X_test, y_test, n_repeats=10, random_state=0, scoring='neg_mean_squared_error')
#r.importances_mean


# In[164]:


#Plot the feature importance plot
feature_importance = pd.DataFrame({'Feature': X.columns[0:10], 'Importance': r.importances_mean[0:10]})
feature_importance = feature_importance.sort_values('Importance', ascending=True)
feature_importance.plot(x='Feature', y='Importance', kind='barh', figsize=(10, 6))


# In[174]:


#Obtain the ALE plots for the most important features
ale_eff = ale(X=X_test, model=best_rf, feature=["total_3pt_made"], grid_size=50, include_CI=False)


# In[172]:


ale_eff = ale(X=X_test, model=best_rf, feature=["total_shots_made"], grid_size=50, include_CI=False)


# In[ ]:




