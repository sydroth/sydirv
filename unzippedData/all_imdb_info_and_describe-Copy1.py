#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib as plt
import seaborn as sns


# In[6]:


imdb_names = pd.read_csv('imdb.name.basics.csv')
imdb_title_akas = pd.read_csv('imdb.title.akas.csv')
imdb_title_basics = pd.read_csv('imdb.title.basics.csv')
imdb_title_crew = pd.read_csv('imdb.title.crew.csv')
imdb_title_principals = pd.read_csv('imdb.title.principals.csv')
imdb_title_ratings = pd.read_csv('imdb.title.ratings.csv')


# In[10]:


imdb_names.info()


# In[9]:


imdb_names.describe()


# In[26]:


imdb_names.head()


# In[11]:


imdb_title_akas.info()


# In[12]:


imdb_title_akas.describe()


# In[25]:


imdb_title_akas.head()


# In[13]:


imdb_title_basics.info()


# In[14]:


imdb_title_basics.describe()


# In[24]:


imdb_title_basics.head()


# In[15]:


imdb_title_crew.info()


# In[16]:


imdb_title_crew.describe()


# In[23]:


imdb_title_crew.head()


# In[17]:


imdb_title_principals.info()


# In[18]:


imdb_title_principals.describe()


# In[22]:


imdb_title_principals.head()


# In[19]:


imdb_title_ratings.info()


# In[20]:


imdb_title_ratings.describe()


# In[21]:


imdb_title_ratings.head()


# In[ ]:




