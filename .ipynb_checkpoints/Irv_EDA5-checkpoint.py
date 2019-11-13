#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# In[2]:


bo_mojo = pd.read_csv('unzippedData/bom.movie_gross.csv')


# In[3]:


the_numbers = pd.read_csv('unzippedData/tn.movie_budgets.csv')


# In[4]:


#in the-numbers:
#convert release date to date format
#convert dollar figures to int format

the_numbers['release_date']=pd.to_datetime(the_numbers['release_date'])
the_numbers['production_budget'] = the_numbers['production_budget'].str.replace(',', '').str.replace('$', '').astype(int)
the_numbers['domestic_gross'] = the_numbers['domestic_gross'].str.replace(',', '').str.replace('$', '').astype(int)
the_numbers['worldwide_gross'] = the_numbers['worldwide_gross'].str.replace(',', '').str.replace('$', '').astype(int)


# In[5]:


#add column for worldwide profitability
the_numbers['Worldwide Profitability'] = the_numbers['worldwide_gross']/the_numbers['production_budget']


# In[6]:


#add column for domestic profitability
the_numbers['Domestic Profitability'] = the_numbers['domestic_gross']/the_numbers['production_budget']


# In[7]:


imdb_title_basics=pd.read_csv('unzippedData/imdb.title.basics.csv') #movie title, year, runtime, genre


# In[8]:


#in imdb-title-basics:
#only movies aafter 2009 >>> TURNS OUT THIS WAS UNNECESSARY
imdb_title_basics=imdb_title_basics[imdb_title_basics['start_year']>2009] 


# In[9]:


#cut out movies less than 75 minutes, more than 4 hours
imdb_title_basics=imdb_title_basics[~(imdb_title_basics['runtime_minutes']>240) & ~(imdb_title_basics['runtime_minutes']<75)]


# In[10]:


#drop all duplicate movie titles
imdb_title_basics = imdb_title_basics.drop_duplicates('primary_title', keep=False)


# In[11]:


#change imdb-title-basics column name to align with 'the-numbers' data
imdb_title_basics.rename(columns={'primary_title':'movie'}, inplace=True)


# In[12]:


#make only one genre entry per column
imdb_title_basics['Genre 1']=imdb_title_basics['genres'].str.split(',', expand=True)[0]
imdb_title_basics['Genre 2']=imdb_title_basics['genres'].str.split(',', expand=True)[1]
imdb_title_basics['Genre 3']=imdb_title_basics['genres'].str.split(',', expand=True)[2]


# In[13]:


#compile set of genres
genres_1 = list(imdb_title_basics['Genre 1'].unique())
genres_2 = list(imdb_title_basics['Genre 2'].unique())
genres_3 = list(imdb_title_basics['Genre 3'].unique())
genre_set = set(genres_1 + genres_2 + genres_3)


# In[14]:


the_numbers.set_index('movie', inplace=True)


# In[15]:


imdb_title_basics.set_index('movie', inplace=True, drop=False)


# In[16]:


#the-numbers joined with IMDB-title-basics
joined_df = the_numbers.join(imdb_title_basics, how='left') 


# In[17]:


#READ IN THIRD DATASET: IMDB-TITLE-RATINGS
imdb_title_ratings=pd.read_csv('unzippedData/imdb.title.ratings.csv') #average rating, number of votes


# In[18]:


#prepare to combine imdb-title-basics and imdb-title-ratings
imdb_title_basics.set_index('tconst', inplace=True)
imdb_title_ratings.set_index('tconst', inplace=True)


# In[19]:


imdb_combined = imdb_title_ratings.join(imdb_title_basics, how='left') #IMDB-title-ratings + IMDB-title-basics
#imdb_combined.head()


# In[20]:


#can now add earnings/budget information from the-numbers
imdb_combined.set_index('movie', inplace=True)
imdb_combined.info() #~73000 entries
#the_numbers.info() #5782 entries


# In[21]:


#combine the-numbers with the combined IMDB data
the_numbers_imdb_combined = the_numbers.join(imdb_combined, how='left')


# In[22]:


#remove entries that were only from the-numbers and not IMDB
the_numbers_imdb_combined2=the_numbers_imdb_combined[the_numbers_imdb_combined['averagerating'].isna()==False]
#the_numbers_imdb_combined2.info()


# In[23]:


main_df = the_numbers_imdb_combined2
#main_df.head()


# In[24]:


#drop unnecessary columns
#IF THE FOLLOWING RETURNS AN ERROR DON'T WORRY ABOUT IT!!!!!
main_df = main_df.drop(['original_title', 'start_year', 'genres'], axis=1)


# In[25]:


#align movie name column in preparation for join
bo_mojo = bo_mojo.rename(columns={'title':'movie'})
bo_mojo = bo_mojo.set_index('movie')


# In[26]:


#preserve title of movie
bo_mojo['movie']=bo_mojo.index


# In[27]:


#strip movie of ending year-in-parentheses
movie_stripped =[]
for x in bo_mojo.movie:
    if '(' in x:
        movie_stripped.append(x[:(x.find('(')-1)])
    else:
        movie_stripped.append(x)

bo_mojo['movie']=movie_stripped


# In[28]:


#set index as movie without ending year-in-parentheses
bo_mojo.set_index('movie', inplace=True)


# In[29]:


#drop 
bo_mojo.drop(columns=['domestic_gross', 'foreign_gross'], axis=1, inplace=True)
#bo_mojo.head()


# In[30]:


#combine the previous IMDB-thenumbers with bomojo
main_df2=main_df.join(bo_mojo, how='left')
#main_df2.head()


# In[31]:


main_df2.drop(['year'], axis=1, inplace=True)
#main_df2.head()


# In[32]:


main_df3=main_df2


# In[33]:


#restrict release date to 2010-
#restrict production budget to >=$1,000,000
main_df3 = main_df3[main_df3['release_date'].dt.year>2009]
main_df3 = main_df3[main_df3['production_budget']>=1000000]


# In[34]:


#create new category: no studio given is "small studio"
main_df3['studio'].fillna(value='small studio', inplace=True)


# In[35]:


#replace $0 with NaN for worldwide gross
main_df3['worldwide_gross'] = main_df3['worldwide_gross'].replace(0,np.nan)
# s = pd.Series([0, 1, 2, 0, 4])
# s.replace(0, np.nan)


# In[36]:


#create list of Top10 biggest studios plus "small studio"
studio_list=list(main_df3['studio'].value_counts().head(11).index)
biggest_studios_df=main_df3[main_df3['studio'].isin(studio_list)]


# In[37]:


#create plot of profitability by studio
sns.set(font_scale=3)
plt.figure(figsize=(15,10))
result = biggest_studios_df.groupby(["studio"])['Worldwide Profitability'].aggregate(np.mean).reset_index().sort_values('Worldwide Profitability')
ax1 = sns.barplot('studio', 'Worldwide Profitability', data=biggest_studios_df, order=result['studio'], palette=sns.color_palette("coolwarm", len(result)))
plt.title('Profitability by Studio')
plt.xlabel('Studio')
plt.xticks(rotation=45)
plt.ylabel('Worldwide Profitability')
plt.show()


# In[38]:


palette_1 = sns.color_palette("coolwarm", len(result))
result['palette'] = palette_1
palette_df = result.drop(['Worldwide Profitability', 'studio'], axis=1)
#palette_df


# In[39]:


#create plot of 
result = biggest_studios_df.groupby(["studio"])['averagerating'].aggregate(np.mean).reset_index().sort_values('averagerating')
result=result.join(palette_df)


# In[40]:


plt.figure(figsize=(15,10))
ax1 = sns.barplot('studio', 'averagerating', data=biggest_studios_df, order=result['studio'], palette=sns.color_palette(list(result['palette'])))
plt.title('Ratings by Studio')
plt.xlabel('Studio')
plt.xticks(rotation=45)
plt.ylabel('Average Movie Rating')
plt.show()


# In[41]:


#create dictionary with values as genres
genre_dict={}
for i, genre in zip(range(len(genre_set)), genre_set):
        genre_dict[i]=[genre]


# In[42]:


#append to dictionary values for average ratings and of worldwide profitability
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


# In[43]:


#exclude genres with no avilable data
for i in range(29):
    if str(genre_dict[i][1])=='nan':
        del genre_dict[i]
    else:
        pass


# In[44]:


#create dataframe based on genre dictionary
main_genre_df = pd.DataFrame.from_dict(genre_dict, orient='index',columns=['Genre', 'Median Average Ratings', 'Mean Average Ratings','Median Worldwide Profitability', 'Mean Worldwide Profitability'])      


# In[45]:


#plot median rating by genre
plt.figure(figsize=(15,10))
result = main_genre_df.sort_values('Median Average Ratings').reset_index()
ax1 = sns.barplot('Genre', 'Median Average Ratings', data=main_genre_df, order=result['Genre'], palette=sns.color_palette("coolwarm", len(result)))
plt.title('Ratings by Genre')
plt.xlabel('Genre')
plt.xticks(rotation=75)
plt.ylabel('Average Movie Rating')
plt.show()


# In[46]:


palette_1 = sns.color_palette("coolwarm", len(result))
result['palette'] = palette_1
palette_df = result.drop(['Median Average Ratings','Mean Average Ratings', 'Median Worldwide Profitability', 'Mean Worldwide Profitability', 'Genre'], axis=1)
palette_df = palette_df.set_index('index')
#palette_df


# In[47]:


result = main_genre_df.sort_values('Median Worldwide Profitability').reset_index()
result = result.set_index('index')
result = result.join(palette_df)


# In[48]:


#plot median profitability by genre
plt.figure(figsize=(15,10))
ax1 = sns.barplot('Genre', 'Median Worldwide Profitability', data=main_genre_df, order=result['Genre'], palette=sns.color_palette(list(result['palette'])))
plt.title('Profitability by Genre')
plt.xlabel('Genre')
plt.xticks(rotation=75)
plt.ylabel('Worldwide Profitability')
plt.show()


# In[ ]:




