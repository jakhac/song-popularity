# Prediction of a Song's Popularity

Data science approach to predict the popularity of a song using ensemble learning methods for musical, lyrical and artist features. This repository contains the code associated with our term paper.

<p align="center">
  <img alt="Machine learning approach" src="https://user-images.githubusercontent.com/49451811/140611267-c9ee2b6e-7b8a-47cb-ae4d-16abc263ca8b.JPG" />
</p>

## Abstract
*We predicted song popularity using musical and artist features from Spotify data as well as self-computed lyrical
measurements. For each set of features, we trained binary and multiclass classifiers and found the artist-only model to have better
results than the music-only and lyrics-only models. We implemented two ensemble approaches and achieved the overall best result
using a random forest classifier with an accuracy of 82% for binary and 65% for multiclass classification. The most decisive features
ordered by relevance are artist follower count, artist popularity and release year. We found out that only 42% of popular songs would
also be popular if released by an unpopular artist. Consequently, song popularity largely depends on the popularity of an artist.*

## Code
Please note that the code is *not* fully executable without a SQL database populated with the [Spotify dataset](https://www.kaggle.com/yamaerenay/spotify-dataset-19212020-160k-tracks) from Kaggle (Nov 21: not available anymore, use a similar dataset or the [Spotify API](https://developer.spotify.com/documentation/web-api/) directly) and the lyrics corresponding to the songs. We do not publish the database, however its structure can be re-created by running the `db_setup.py` script and then using the scripts in the `dataset` folder to populate it. To work with lyrics, a [Genius API](https://docs.genius.com/) key will be required. 

## Contributors
**Kevin Katzkowski** - [GitHub](https://github.com/katzkowski)   
**Jakob Hackstein** - [GitHub](https://github.com/jakhac)   
**Luca D'Agostino**  
