import bs4
import os
import json
import re

# WIKI_PAGE = 'https://animalcrossing.fandom.com/wiki/DIY_recipes'
FILE_LOCATION = os.path.dirname(__file__)

with open(os.path.join(FILE_LOCATION, 'diy_recipes.html'), 'r') as recipe_html:
    page_contents = recipe_html.read()

soup = bs4.BeautifulSoup(page_contents, 'html.parser')

table_tr_collection = soup.select('.article-table tbody tr')

data = {}
recipes = data.setdefault('recipes', [])

for recipe_tr in table_tr_collection:
    recipe = {}
    recipes.append(recipe)

    cells = recipe_tr.select('td')

    recipe_name_cell = cells[0]
    recipe_image_cell = cells[1]
    recipe_materials_cell = cells[2]

    if len(cells) >= 6:
        recipe_footprint_cell = cells[3]
        recipe_source_cell = cells[4]
        recipe_sell_price_cell = cells[5]
    else:
        recipe_footprint_cell = None
        recipe_source_cell = cells[3]
        recipe_sell_price_cell = cells[4]

    recipe_name = cells[0].text.strip()
    recipe['name'] = recipe_name

    mult_factor_regex = re.search(r'x(\d+)$', recipe_name, re.I)

    try:
        if mult_factor_regex:
            recipe_sell_price_mult_factor = int(mult_factor_regex.group(1))
        else:
            recipe_sell_price_mult_factor = 1
    except:
        recipe_sell_price_mult_factor = 1

    recipe_name_a = cells[0].find('a')

    # Will be used to determine if the recipe has a valid URL (<a> will have a
    # "class" of "new")
    recipe_url_class = (
        recipe_name_a.attrs.get('class', [])
        if recipe_name_a else
        []
    )

    recipe['has_page'] = 'new' not in recipe_url_class

    recipe['url'] = (
        recipe_name_a.attrs.get('href', None)
        if recipe_name_a else
        None
    )

    recipe_image_a = recipe_image_cell.find('a')
    recipe['image_url'] = (
        recipe_image_a.attrs.get('href', None)
        if recipe_image_a else
        None
    )

    materials = recipe.setdefault('materials', [])

    if len(cells) <= 2:
        continue

    recipe_materials_a = recipe_materials_cell.select('a:not(.image)')
    for material_a in recipe_materials_a:
        material = {}
        materials.append(material)
        material['name'] = material_a.text.strip()
        material['url'] = material_a.attrs.get('href', None)

        current_node = material_a
        while current_node and not isinstance(current_node, str):
            current_node = current_node.previous_sibling
        try:
            material['quantity'] = int(current_node.strip().strip('x'))
        except:
            material['quantity'] = 1

    recipe['recipe_source'] = recipe_source_cell.text.strip()

    sell_price = recipe_sell_price_cell.text.strip()
    try:
        recipe_sell_price = int(re.sub(r'[^\d]', '', sell_price))
    except:
        recipe_sell_price = None
    
    recipe['sell_price'] = (
        recipe_sell_price * recipe_sell_price_mult_factor
        if recipe_sell_price and recipe_sell_price_mult_factor else
        None
    )

with open(os.path.join(FILE_LOCATION, 'diy_recipes.json'), 'w') as recipe_json:
    json.dump(data, recipe_json, indent=2)
