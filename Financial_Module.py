#!/usr/bin/env python
# coding: utf-8

# ## Import the Libraries

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# ## Read in the Data

# In[2]:


the_numbers = pd.read_csv('unzippedData/tn.movie_budgets.csv')
bo_mojo = pd.read_csv('unzippedData/bom.movie_gross.csv')
imdb_title_basics=pd.read_csv('unzippedData/imdb.title.basics.csv') #movie title, year, runtime, genre
imdb_title_ratings=pd.read_csv('unzippedData/imdb.title.ratings.csv') #average rating, number of votes


# ## Clean the initial 'the-numbers.com' dataset:
# - Convert date strings to datetime
# - Convert dollar-figure strings to integer
# - Create new columns for Domestic and Worldwide Profitability

# In[3]:


the_numbers['release_date']=pd.to_datetime(the_numbers['release_date'])
the_numbers['production_budget'] = the_numbers['production_budget'].str.replace(',', '').str.replace('$', '').astype(int)
the_numbers['domestic_gross'] = the_numbers['domestic_gross'].str.replace(',', '').str.replace('$', '').astype(int)
the_numbers['worldwide_gross'] = the_numbers['worldwide_gross'].str.replace(',', '').str.replace('$', '').astype(int)
the_numbers['Worldwide Profitability'] = the_numbers['worldwide_gross']/the_numbers['production_budget']
the_numbers['Domestic Profitability'] = the_numbers['domestic_gross']/the_numbers['production_budget']


# ## Clean the initial IMDB dataset:
# - Eliminate films made before 2010
# - Eliminate films with runtimes under 75 minutes
# - Eliminate films with runtimes over 240 minutes
# - Rename column titles to match 'the-numbers.com' dataset
# - Create a set of unique genres

# In[4]:


imdb_title_basics=imdb_title_basics[imdb_title_basics['start_year']>2009] 
imdb_title_basics=imdb_title_basics[~(imdb_title_basics['runtime_minutes']>240) & ~(imdb_title_basics['runtime_minutes']<75)]
imdb_title_basics = imdb_title_basics.drop_duplicates('primary_title', keep=False)
imdb_title_basics.rename(columns={'primary_title':'movie'}, inplace=True)
imdb_title_basics['Genre 1']=imdb_title_basics['genres'].str.split(',', expand=True)[0]
imdb_title_basics['Genre 2']=imdb_title_basics['genres'].str.split(',', expand=True)[1]
imdb_title_basics['Genre 3']=imdb_title_basics['genres'].str.split(',', expand=True)[2]
genres_1 = list(imdb_title_basics['Genre 1'].unique())
genres_2 = list(imdb_title_basics['Genre 2'].unique())
genres_3 = list(imdb_title_basics['Genre 3'].unique())
genre_set = set(genres_1 + genres_2 + genres_3)


# ## Join 'the-numbers.com' data with IMDB Title data into Master Dataframe

# In[5]:


the_numbers.set_index('movie', inplace=True)
imdb_title_basics.set_index('movie', inplace=True, drop=False)
joined_df = the_numbers.join(imdb_title_basics, how='left') 


# ## Join IMDB Ratings data into Master Dataframe

# In[6]:


imdb_title_basics.set_index('tconst', inplace=True)
imdb_title_ratings.set_index('tconst', inplace=True)
imdb_combined = imdb_title_ratings.join(imdb_title_basics, how='left')
imdb_combined.set_index('movie', inplace=True)
the_numbers_imdb_combined = the_numbers.join(imdb_combined, how='left')
main_df=the_numbers_imdb_combined[the_numbers_imdb_combined['averagerating'].isna()==False]


# ## More Cleaning
# - Drop unnecessary/duplicative columns
# - Remove '(YYYY)' from Movie Name

# In[7]:


main_df = main_df.drop(['original_title', 'start_year', 'genres'], axis=1)
bo_mojo = bo_mojo.rename(columns={'title':'movie'})
bo_mojo = bo_mojo.set_index('movie')
bo_mojo['movie']=bo_mojo.index
movie_stripped =[]
for x in bo_mojo.movie:
    if '(' in x:
        movie_stripped.append(x[:(x.find('(')-1)])
    else:
        movie_stripped.append(x)


# ## Join Box Office Mojo studio data to Master Dataframe

# In[8]:


bo_mojo['movie']=movie_stripped
bo_mojo.set_index('movie', inplace=True)
bo_mojo.drop(columns=['domestic_gross', 'foreign_gross'], axis=1, inplace=True)
main_df2=main_df.join(bo_mojo, how='left')
main_df2.drop(['year'], axis=1, inplace=True)
main_df3=main_df2


# ## Further Refine the Data
# - Cut films with budget less than \$1 million
# - Classify films without film studio information as "small studio"
# - Replace '$0' revenue figure with 'NaN'

# In[9]:


main_df3 = main_df3[main_df3['release_date'].dt.year>2009]
main_df3 = main_df3[main_df3['production_budget']>=1000000]
main_df3['studio'].fillna(value='small studio', inplace=True)
main_df3['worldwide_gross'] = main_df3['worldwide_gross'].replace(0,np.nan)
