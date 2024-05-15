This project is a new interface for the BirdNET-Pi Project based on Streamlit

You should ad the following into your secrets.toml:

``` Console
flickr_api = "[optional]"

[connections.birds_db]
url = "sqlite:///../BirdNet-Pi/scripts/birds.db"
```
First you need to pull the repository
``` Console
git pull https://github.com/mazze84/Birdnet-Analyzer.git
```
You can run install.sh to create the environment and install the neccessary libs
After that you can start it with start.sh
