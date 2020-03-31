import collections
import os
import json
import re

import bs4


# WIKI_PAGE = 'https://animalcrossing.fandom.com/wiki/DIY_recipes'
FILE_LOCATION = os.path.dirname(__file__)


def convert_name_to_id(value: str) -> str:
    """
    Converts a value to the common formatting for an enumeration_value:
    1. all characters are converted to lowercase
    2. all numbers, letters, and underscores are kept
    3. all other characters are replaced by underscores
    4. extra underscores are removed from the ends
    5. continuous runs of underscore characters are shortened to "_"
    `"_1 - Some Value - w/ Formatting..."` -> `"1_some_value_w_formatting"`
    """
    value = value.lower()
    value = re.sub(r'[^\w]+', '_', value)
    value = value.strip(' _')
    value = re.sub(r'_+', '_', value)
    return value


with open(os.path.join(FILE_LOCATION, 'diy_recipes.html'), 'r') as recipe_html:
    page_contents = recipe_html.read()

soup = bs4.BeautifulSoup(page_contents, 'html.parser')

table_tr_collection = soup.select('.article-table tbody tr')

recipes = []
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
    recipe['id'] = convert_name_to_id(recipe['name'])

    multiplication_factor_regex = re.search(r'x(\d+)$', recipe_name, re.I)

    try:
        if multiplication_factor_regex:
            recipe_sell_price_multiplication_factor = int(multiplication_factor_regex.group(1))
        else:
            recipe_sell_price_multiplication_factor = 1
    except:
        recipe_sell_price_multiplication_factor = 1

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
        material['id'] = convert_name_to_id(material['name'])
        material['url'] = material_a.attrs.get('href', None)

        current_node = material_a
        while current_node and not isinstance(current_node, str):
            current_node = current_node.previous_sibling

        try:
            material['quantity'] = int(current_node.strip().strip('x'))
        except:
            print(f'WARNING: Issue occurred while scraping quantity of {material} for {recipe}')
            material['quantity'] = 1

    recipe['source'] = recipe_source_cell.text.strip()

    sell_price = recipe_sell_price_cell.text.strip()
    try:
        recipe_sell_price = int(re.sub(r'[^\d]', '', sell_price))
    except:
        recipe_sell_price = None
    
    recipe['sell_price'] = (
        recipe_sell_price * recipe_sell_price_multiplication_factor
        if recipe_sell_price and recipe_sell_price_multiplication_factor else
        None
    )

    recipe['total_crafting_steps'] = 1

recipe_id_map = {}
for recipe in recipes:
    duplicate_recipe = recipe_id_map.get(recipe['id'], None)
    if duplicate_recipe:
        def _reconcile_property(property_name):
            p1 = recipe.get(property_name, None)
            p2 = duplicate_recipe.get(property_name, None)
            if p1 and p2 and p1 != p2:
                print(f"WARNING: Duplicate recipe names with differing {property_name}: {recipe['name']}")

            if (not p2) and p1:
                duplicate_recipe[property_name] = p1

        _reconcile_property('materials')
        _reconcile_property('sell_price')
        _reconcile_property('image_url')

        s1 = recipe['source']
        s2 = duplicate_recipe['source']

        duplicate_recipe['source'] = (
            '\n'.join((s1, s2)) if (s1 and s2) else
            s1 or
            s2 or
            None
        )

        if not duplicate_recipe['has_page'] and recipe['has_page']:
            duplicate_recipe['has_page'] = True
            duplicate_recipe['url'] = recipe['url']
        elif duplicate_recipe['has_page'] and recipe['has_page']:
            _reconcile_property('url')

    else:
        recipe_id_map[recipe['id']] = recipe

recipes = recipe_id_map
del recipe_id_map

adjusted_recipes = set()

def adjust_recipe(recipe: dict):
    if recipe['id'] in adjusted_recipes:
        return

    adjusted_recipes.add(recipe['id'])

    depends_on = recipe.setdefault('depends_on', {recipe['id']})
    raw_materials = recipe.setdefault('raw_materials', {})

    def _add_raw_material(material: dict, quantity: int = 1):
        raw_material = raw_materials.setdefault(
            material['id'],
            {
                'name': material['name'],
                'id': material['id'],
                'url': material['url'],
                'quantity': 0,
            }
        )

        raw_material['quantity'] += quantity * material['quantity']

    for material in recipe['materials']:
        depends_on_recipe = recipes.get(material['id'], None)
        if depends_on_recipe:
            adjust_recipe(depends_on_recipe)

            for do in depends_on_recipe['depends_on']:
                depends_on.add(do)

            recipe['total_crafting_steps'] += (
                material['quantity'] *
                depends_on_recipe['total_crafting_steps']
            )

            for _, raw_material in depends_on_recipe['raw_materials'].items():
                _add_raw_material(raw_material, material['quantity'])

        else:
            _add_raw_material(material)
 
    recipe['depends_on'] = list(recipe['depends_on'])

for _, recipe in recipes.items():
    adjust_recipe(recipe)

raw_materials = {}

for recipe in recipes.values():
    for raw_material_id, raw_material in recipe['raw_materials'].items():
        duplicate_raw_material = raw_materials.get(raw_material_id, None)

        def _reconcile_property(property_name):
            p1 = raw_material.get(property_name, None)
            p2 = duplicate_raw_material.get(property_name, None)
            if p1 and p2 and p1 != p2:
                print(f"WARNING: Duplicate raw material names with differing {property_name}: Recipe \"{recipe['name']}\" Raw Material: \"{raw_material['name']}\"")

            if (not p2) and p1:
                duplicate_raw_material[property_name] = p1

        if duplicate_raw_material:
            _reconcile_property('url')
            duplicate_raw_material['used_in'].append(recipe['id'])

        else:
            raw_materials[raw_material_id] = {
                'name': raw_material['name'],
                'id': raw_material['id'],
                'url': raw_material['url'],
                'used_in': [recipe['id']],
            }

# TODO: Calculate value contributed to sell_price when involved in a "typical
#       crafted recipe"

# TODO: Calculate estimated_sell_price for all recipes even if sell_price is
#       None

# TODO: Look for recipes whose sell prices are not derived from the materials
#       that are put in (enumeration: normal, lower, higher)

data = {
    'recipes': recipes,
    'raw_materials': raw_materials,
}

with open(os.path.join(FILE_LOCATION, 'diy_recipes.json'), 'w') as recipe_json:
    json.dump(data, recipe_json, indent=2)
