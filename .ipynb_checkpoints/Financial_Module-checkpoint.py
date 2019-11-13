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


# ## Create dataframe with information from the Top Ten biggest studios

# In[10]:


studio_list=list(main_df3['studio'].value_counts().head(11).index)
biggest_studios_df=main_df3[main_df3['studio'].isin(studio_list)]


# ## Plot Profitability by Studio

# In[11]:


sns.set(font_scale=3)
plt.figure(figsize=(15,10))
result = biggest_studios_df.groupby(["studio"])['Worldwide Profitability'].aggregate(np.mean).reset_index().sort_values('Worldwide Profitability')
ax1 = sns.barplot('studio', 'Worldwide Profitability', data=biggest_studios_df, order=result['studio'], palette=sns.color_palette("coolwarm", len(result)))
plt.title('Profitability by Studio')
plt.xlabel('Studio')
plt.xticks(rotation=45)
plt.ylabel('Worldwide Profitability')
plt.show()


# ## Save color assignments

# In[12]:


palette_1 = sns.color_palette("coolwarm", len(result))
result['palette'] = palette_1
palette_df = result.drop(['Worldwide Profitability', 'studio'], axis=1)


# ## Plot Average Rating by Studio

# In[13]:


result = biggest_studios_df.groupby(["studio"])['averagerating'].aggregate(np.mean).reset_index().sort_values('averagerating')
result=result.join(palette_df)
plt.figure(figsize=(15,10))
ax1 = sns.barplot('studio', 'averagerating', data=biggest_studios_df, order=result['studio'], palette=sns.color_palette(list(result['palette'])))
plt.title('Ratings by Studio')
plt.xlabel('Studio')
plt.xticks(rotation=45)
plt.ylabel('Average Movie Rating')
plt.show()


# ## Create Dataframe containing information according to Genre

# In[14]:


#Start with a dictionary
genre_dict={}
for i, genre in zip(range(len(genre_set)), genre_set):
        genre_dict[i]=[genre]
for i in range(29):
    genre_df_current = main_df3[(main_df3['Genre 1']==genre_dict[i][0]) | (main_df3['Genre 2']==genre_dict[i][0]) | (main_df3['Genre 3']==genre_dict[i][0])]
    median_average_ratings = genre_df_current['averagerating'].median()
    mean_average_ratings = genre_df_current['averagerating'].mean()
    median_worldwide_profitability = genre_df_current['Worldwide Profitability'].median()
    mean_worldwide_profitability = genre_df_current['Worldwide Profitability'].mean()
    genre_dict[i].append(median_average_ratings)
    genre_dict[i].append(mean_average_ratings)
    genre_dict[i].append(median_worldwide_profitability)
    genre_dict[i].append(mean_worldwide_profitability)

#exclude genres with no avilable data
for i in range(29):
    if str(genre_dict[i][1])=='nan':
        del genre_dict[i]
    else:
        pass

#create dataframe based on  dictionary
main_genre_df = pd.DataFrame.from_dict(genre_dict, orient='index',columns=['Genre', 'Median Average Ratings', 'Mean Average Ratings','Median Worldwide Profitability', 'Mean Worldwide Profitability'])      


# ## Plot Average Movie Rating by Genre

# In[15]:


sns.set(font_scale=3)
plt.figure(figsize=(15,10))
result = main_genre_df.sort_values('Median Average Ratings').reset_index()
ax1 = sns.barplot('Genre', 'Median Average Ratings', data=main_genre_df, order=result['Genre'], palette=sns.color_palette("coolwarm", len(result)))
plt.title('Ratings by Genre')
plt.xlabel('Genre')
plt.xticks(rotation=75)
plt.ylabel('Average Movie Rating')
plt.show()


# ## Save color assignments

# In[16]:


palette_1 = sns.color_palette("coolwarm", len(result))
result['palette'] = palette_1
palette_df = result.drop(['Median Average Ratings','Mean Average Ratings', 'Median Worldwide Profitability', 'Mean Worldwide Profitability', 'Genre'], axis=1)
palette_df = palette_df.set_index('index')


# ## Plot Profitability by Genre

# In[17]:


result = main_genre_df.sort_values('Median Worldwide Profitability').reset_index()
result = result.set_index('index')
result = result.join(palette_df)
plt.figure(figsize=(15,10))
ax1 = sns.barplot('Genre', 'Median Worldwide Profitability', data=main_genre_df, order=result['Genre'], palette=sns.color_palette(list(result['palette'])))
plt.title('Profitability by Genre')
plt.xlabel('Genre')
plt.xticks(rotation=75)
plt.ylabel('Worldwide Profitability')
plt.show()


# ## this is my title
# - first point

# In[18]:


1==0


# - second point

# In[ ]:




