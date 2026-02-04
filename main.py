import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main():
  global movies

  movies = pd.read_csv("sample_data/movies.csv")
  movies = handleNullValues()

  highestLowestGrossingMovies()   #Additional CSV
  highestLowestRatedMovies()    #Line Chart
  totalMoviesInDecade()   #Bar Graph
  genreWiseMovies()   #Pie Chart
  multipleGenreMovies()   #Value is printed directly
  numberOfMoviesByDirector()    #Additional CSV
  topRatedMovies(10)    #Numpy Array

def handleNullValues():
  print("The dataframe has a total of", len(movies.index), "rows")
  print("The null values in each column are", movies.isnull().sum())    #Check for the null values in the dataset

  updatedMovies = movies.drop("MetaScore", axis=1)    #Drop the column having null values
  updatedMovies.dropna(inplace=True)    #Drop rows which contain null values

  print("After dropping the column and removing null valued rows, we have a total of", len(updatedMovies.index), "rows")

  return updatedMovies

def groupByColumns(groupBy, columnOn, type, resetIndex=False):
  ###
  #This function groups the data by column and gets the min, max or count based on the given arguments
  ###
  newDF = ''
  if type == 'max':
    newDF = movies.groupby(groupBy)[columnOn].max()
  elif type == 'min':
    newDF = movies.groupby(groupBy)[columnOn].min()
  elif type == 'count':
    newDF = movies.groupby(groupBy)[columnOn].count()
  elif type == 'idxmax':
    newDF = movies.loc[movies.groupby(groupBy)[columnOn].idxmax()]
  elif type == 'idxmin':
    newDF = movies.loc[movies.groupby(groupBy)[columnOn].idxmin()]

  if resetIndex:
    newDF = newDF.reset_index()
  return newDF

def groupYearsIntoDecades(year):
  ###
  # Calculates the deacade of the given year
  ###
  return str(year // 10 * 10) + 's'

def convertToList(stringValue):
  ###
  # Converts multiple comma separated string values into an array
  ###
  return [value.strip(" '[]") for value in stringValue.split(',')]

def highestLowestGrossingMovies():
  maxGrossMovies = groupByColumns('Year of Release', 'Gross', 'idxmax', True)
  minGrossMovies = groupByColumns('Year of Release', 'Gross', 'idxmin', True)

  #Renaming the columns as required
  maxGrossDF = maxGrossMovies.rename(columns={"Gross": "Highest Gross", "Movie Name": "Highest Gross Movie"})
  minGrossDF = minGrossMovies.rename(columns={"Gross": "Lowest Gross", "Movie Name": "Lowest Gross Movie"})

  #Fetching the required columns from the whole dataframe
  maxGrossDF = maxGrossDF[['Year of Release', 'Highest Gross Movie', 'Highest Gross']]
  minGrossDF = minGrossDF[['Year of Release', 'Lowest Gross Movie', 'Lowest Gross']]

  #Merging two dataframes
  mergedDF = pd.merge(maxGrossDF, minGrossDF, on='Year of Release')

  #Exporting to an additional CSV file
  combinedCSVPath = 'highest_lowest_gross_movies_by_year.csv'
  mergedDF.to_csv(combinedCSVPath, index=False)
  print(" ")

def highestLowestRatedMovies():
  maxRatedDF = groupByColumns('Certification', 'Movie Rating', 'max', True)
  minRatedDF = groupByColumns('Certification', 'Movie Rating', 'min', True)

  plt.figure(figsize=(10, 6))

  #Plotting the graphs and naming the x and y axis
  plt.plot(maxRatedDF['Certification'], maxRatedDF['Movie Rating'], label='Highest Rating', color='blue')
  plt.plot(minRatedDF['Certification'], minRatedDF['Movie Rating'], label='Lowest Rating', color='red')

  plt.title('Highest and Lowest Movie Ratings per Certification')
  plt.xlabel('Certification')
  plt.ylabel('Movie Rating')
  plt.legend()
  plt.xticks(rotation=45, ha='right')
  plt.show()

  print(" ")

def totalMoviesInDecade():
  movies['Decade'] = movies['Year of Release'].apply(groupYearsIntoDecades)   #Calculating the decade of a particular year

  moviesInDecade = groupByColumns('Decade', 'Movie Name', 'count', True)

  plt.figure(figsize=(10, 6))
  bars = plt.bar(moviesInDecade['Decade'], moviesInDecade['Movie Name'], color='blue')
  plt.xlabel('Decade')
  plt.ylabel('Total Number of Movies')
  plt.title('Total Number of Movies in each Decade')

  plt.xticks(rotation=45, ha='right')

  #Calculating the values to show on the top of bars of bar chart
  for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), ha='center', va='bottom')

  plt.show()

  print(" ")

def genreWiseMovies():
  movies['Genre'] = movies['Genre'].apply(convertToList)    #Converting the comma separated string values into an array

  allGenres = [genre for genres in movies['Genre'] for genre in genres]

  genresDF = pd.DataFrame({'Genre': allGenres})
  highRatedMovies = movies[movies['Movie Rating'] > 8]
  highRatedGenres = [genre for genres in highRatedMovies['Genre'] for genre in genres]    #Splitting multiple genres for count

  genreCount = pd.Series(highRatedGenres).value_counts()

  plt.figure(figsize=(20, 15))
  plt.pie(genreCount, labels=genreCount.index, autopct='%1.1f%%', startangle=140, pctdistance=0.85)
  plt.title('Distribution of Genres for Movies with Rating > 8')
  # plt.legend(loc='upper right')
  plt.show()

  print(" ")

def multipleGenreMovies():
  #Count the genres in each row
  movies['Multiple Genres'] = movies['Genre'].apply(lambda x: len(x) if isinstance(x, list) else 1)

  totalSum = (movies['Multiple Genres'] > 1).sum()

  print("The number of movies which have multiple genres is", totalSum)

def numberOfMoviesByDirector():
  movies['Director'] = movies['Director'].apply(convertToList)  #Converting the comma separated string values into an array

  allDirectors = [director for directorsList in movies['Director'] for director in directorsList]

  directorDF = pd.DataFrame({'Director': allDirectors})
  directorCount = directorDF['Director'].value_counts().reset_index()
  directorCount.columns = ['Director', 'Number of Movies']

  #Exporting the data to additional CSV
  directorCount.to_csv('director_count.csv', header=True, index=False)

  print(" ")

def topRatedMovies(topCount):
  movies['Year of Release'] = pd.to_datetime(movies['Year of Release'], format='%Y')

  #Filtering out the movies based on conditions
  filteredMovies = movies[(movies['Year of Release'] > pd.Timestamp.now() - pd.DateOffset(years=5)) &
                          (movies['Run Time in minutes'] > 120) &
                          (movies['Votes'] > 10000)]

  topRatedMovies = filteredMovies.sort_values(by='Movie Rating', ascending=False).head(topCount)
  topRatedArray = topRatedMovies[['Movie Name', 'Movie Rating']].to_numpy()
  np.save("top_rated_movies.npy", topRatedArray)    #Save data to numpy array

  print("The top rated movies are:\n", topRatedArray)

  print(" ")

if __name__ == "__main__":
  main()