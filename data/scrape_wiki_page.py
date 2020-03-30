import bs4
import os
import json

# WIKI_PAGE = "https://animalcrossing.fandom.com/wiki/DIY_recipes"
FILE_LOCATION = os.path.dirname(__file__)

with open(os.path.join(FILE_LOCATION, "diy_recipes.html")) as recipe_html:
    page_contents = recipe_html.read()

soup = bs4.BeautifulSoup(page_contents, "html.parser")

recipes = soup.select(".article-table tbody tr")

data = []
for recipe in recipes:
    record = {}
    data.append(record)

    cells = recipe.select("td")

    record['name'] = cells[0].text.strip()

    recipe_name_a = cells[0].find('a')

    # Will be used to determine if the recipe has a valid URL (<a> will have a
    # "class" of "new")
    recipe_url_class = (
        recipe_name_a.attrs.get('class', None)
        if recipe_name_a else
        None
    )

    record['url'] = (
        recipe_name_a.attrs.get('href', None)
        if recipe_name_a else
        None
    )

    recipe_image_a = cells[1].find('a')
    record['image_url'] = (
        recipe_name_a.attrs.get('href', None)
        if recipe_image_a else
        None
    )

    record['ingredients'] = []
    recipe_ingredients = cells[2].select('a')

    # TODO: Scrape materials and quantities from recipe_ingredients

    # TODO: Scrape cost if available (None meaning "this data still needs to
    # be crowd-sourced")
    record['cost'] = None

    # TODO: Scrape "Notes" (usually recipe source)
    record['notes'] = None

# TODO: Dump data to a JSON file. Possibly include date generated and source of
# data

print(data)
