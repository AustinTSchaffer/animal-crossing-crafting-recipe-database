# AC:NH Recipes Application Data

This sub-project is used to gather and generate data for the broader application
by scraping the HTML pages for the following URLs:

- https://animalcrossing.fandom.com/wiki/DIY_recipes
- https://animalcrossing.fandom.com/wiki/Crafting_materials_(New_Horizons)

The script uses Selenium (Firefox) to download and prepare the pages for
scraping. For running app.py locally, please refer to the relevant documentation
for installing Firefox or Firefox ESR and Geckodriver.

Alternatively, this directory contains the necessary infrastructure to easily
install and run the script in a container, using Docker / Docker-Compose. For
that operation:

```bash
# With docker-compose
docker-compose up --build

# Without docker-compose
docker image build -t austintschaffer/acno-recipes-webscraper .
docker container run \
    -v "$(pwd)/diy_recipes.json:/diy_recipes.json" \
    --rm \
    --shm-size="2gb" \
    austintschaffer/acno-recipes-webscraper
```
