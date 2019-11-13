#!/usr/bin/env python
# coding: utf-8

# # Question 1: Do geographical boundaries affect audience reception of runtimes? Have there been any changing trends?

# In[1]:


import pandas as pd
import numpy as np
import matplotlib as plt
import seaborn as sns


# In[2]:


imdb_title_akas = pd.read_csv('unzippedData/imdb.title.akas.csv')
imdb_title_basics = pd.read_csv('unzippedData/imdb.title.basics.csv')
imdb_title_ratings = pd.read_csv('unzippedData/imdb.title.ratings.csv')
#bo_mojo = pd.read_csv('unzippedData/bom.movie_gross.csv')
#rt_movies= pd.read_csv('unzippedData/rt.movie_info.tsv', sep='\t', index_col=False, encoding = 'unicode_escape')
#rt_reviews = pd.read_csv('unzippedData/rt.reviews.tsv', sep='\t', index_col=False, encoding = 'unicode_escape')
#the_numbers = pd.read_csv('unzippedData/tn.movie_budgets.csv')
#theMovieDB = pd.read_csv('unzippedData/tmdb.movies.csv')


# ### We need the following information from these tables:
#  - imdb_title_akas - tconst, region
#  - imdb_title_basics - tconst, primary_title, start_year, runtime_minutes
#  - imdb_title_ratings - tconst, averagerating, numvotes  

# In[3]:


# Rename "title_id" column in imdb_title_akas as "tconst"- 
# these are the same values across all IMDB tables but are named weirdly.
# This also sets tconst as index, which we'll need to ensure matching tables

imdb_title_akas.rename(columns = {'title_id':'tconst'}, inplace=True) 


# In[4]:


# Set "tconst" as index in imdb_title_akas.

imdb_title_akas.set_index('tconst', inplace=True)


# In[5]:


# Set "tconst" as index in imdb_title_basics.

imdb_title_basics.set_index('tconst', inplace=True)


# In[6]:


# Set "tconst" as index in imdb_title_ratings.

imdb_title_ratings.set_index('tconst', inplace=True)


# In[7]:


# Boil a imdb_title_basics down to only the primary_title, start_year, and runtime_minutes columns.

trimmed_basics_df = imdb_title_basics.drop(['genres', 'original_title'], axis=1)


# In[8]:


#new big table should have title, run time, ratings, region

basics_merge_akas_df = trimmed_basics_df.merge(imdb_title_akas['region'],how='left', left_index=True, right_index=True)


# In[9]:


basics_merge_akas_df.head(5)


# In[10]:


#create column 'rating_percent' which is 'averagerating' as a percentage.
imdb_title_ratings['rating_percent'] = (imdb_title_ratings['averagerating'] * 10)


# In[11]:


trimmed_imdb_ratings_df = imdb_title_ratings.drop(['averagerating', 'numvotes'], axis=1)


# In[12]:


# Merge our new rating percent table into our basics_merge_akas
#table to create our final runtime_comparisons table.
runtimes_df = basics_merge_akas_df.merge(trimmed_imdb_ratings_df, how='left', left_index=True, right_index=True)


# In[13]:


runtimes_df.head(10)


# In[14]:


# Rename start_year column as release_year in runtimes_df.
runtimes_df.rename(columns = {'start_year':'release_year'}, inplace=True) 


# In[15]:


# Rename primary_title column as title in runtimes_df.
runtimes_df.rename(columns = {'primary_title':'title'}, inplace=True)


# In[16]:


runtimes_df = runtimes_df[~runtimes_df.index.duplicated(keep='first')]
#runtimes_df


# In[17]:


runtimes_df.info()


# In[18]:


# Replace 0 values in runtimes_df['release_year'] with NaN
runtimes_df.release_year.replace(0, np.NaN)


# In[19]:


# Replace 0 values in runtimes_df['runtime_minutes'] with NaN
runtimes_df.runtime_minutes.replace(0, np.NaN)


# In[20]:


# Replace 0 values in runtimes_df['rating_percent'] with NaN
runtimes_df.rating_percent.replace(0, np.NaN)


# In[21]:


# Drop rows with any NaN values; all columns are needed for analysis.
runtimes_df = runtimes_df.dropna()


# In[22]:


runtimes_df.info()


# In[23]:


runtimes_df.release_year.astype(int, inplace=True)


# In[27]:


# Remove everything outside of 2010 - 2018.
#runtimes_df.head()
# df.drop(df[df['Age'] < 25].index, inplace = True) 

runtimes_df.drop(runtimes_df[runtimes_df['release_year'] > 2018].index, inplace=True) 


# In[29]:


runtimes_df.head(30)


# In[26]:


### HEADCANNONS
# imdb_title_basics=imdb_title_basics[~(imdb_title_basics['runtime_minutes']>240) & ~(imdb_title_basics['runtime_minutes']<75)]
#imdb_title_basics = imdb_title_basics.drop_duplicates('primary_title', keep=False)
#imdb_title_basics['primary_title'].value_counts()
#imdb_title_basics.rename(columns={'primary_title':'movie'}, inplace=True)
#imdb_title_basics.head()
#imdb_combined = imdb_title_ratings.join(imdb_title_basics, how='left') #IMDB-title-ratings + IMDB-title-basics
#imdb_combined.head()
# imdb_title_akas - title, region
# imdb_title_basics - primary_title, start_year, runtime_minutes
# imdb_title_ratings - tconst, averagerating, numvotes  
# bo_mojo - title, domestic_gross,foreign_gross, year
# the_numbers - movie, domestic_gross, worldwide_gross, release_year ((the_numbers['release_year']=the_numbers['release_date'].dt.year))
# theMovieDB - title, release_date, vote_average, vote_count

