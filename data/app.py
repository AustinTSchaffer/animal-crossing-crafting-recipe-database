import datetime
import collections
import os
import json
import re

import bs4
import selenium.webdriver
import selenium.webdriver.support.expected_conditions

WIKI_BASE_URL = 'https://animalcrossing.fandom.com'
WIKI_PAGES_DIY_RECIPES = [
    'https://animalcrossing.fandom.com/wiki/DIY_recipes',
    'https://animalcrossing.fandom.com/wiki/DIY_recipes/Tools',
    'https://animalcrossing.fandom.com/wiki/DIY_recipes/Housewares',
    'https://animalcrossing.fandom.com/wiki/DIY_recipes/Miscellaneous',
    'https://animalcrossing.fandom.com/wiki/DIY_recipes/Wall-mounted',
    'https://animalcrossing.fandom.com/wiki/DIY_recipes/Wallpaper,_rugs_and_flooring',
    'https://animalcrossing.fandom.com/wiki/DIY_recipes/Equipment',
    'https://animalcrossing.fandom.com/wiki/DIY_recipes/Other',
]

WIKI_PAGE_CRAFTING_MATERIALS = 'https://animalcrossing.fandom.com/wiki/Crafting_materials_(New_Horizons)'

FILE_LOCATION = os.path.dirname(__file__)


def convert_name_to_id(value: str) -> str:
    """
    In order to prevent duplication of recipes and raw materials caused by
    variations in casing, spacing, and special characters, this function
    converts names to identifiers using the following formatting:

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


def load_html_page(page: str) -> str:
    """
    Loads a string containing the HTML representation of the requested page.
    """

    print("Downloading:", page)

    options = selenium.webdriver.firefox.options.Options()
    options.headless = True
    browser = selenium.webdriver.Firefox(options=options)
    browser.get(page)

    page_contents = browser.page_source
    print('Page:', page, 'Source Length:', len(page_contents))
    return page_contents


def scrape_recipes_from_html_doc(page_contents: str) -> list:
    """
    Converts the diy_recipes.html document to a list of dicts that represent
    that data from those recipes.
    """

    recipes = []
    soup = bs4.BeautifulSoup(page_contents, 'html.parser')
    table_tr_collection = soup.select('.article-table tbody tr')
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

        recipe_name = recipe_name_cell.text.strip()
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

        recipe_name_a = recipe_name_cell.find('a')

        # Will be used to determine if the recipe has a valid URL (<a> will have a
        # "class" of "new")
        recipe_url_class = (
            recipe_name_a.attrs.get('class', [])
            if recipe_name_a else
            []
        )

        recipe['uri'] = (
            recipe_name_a.attrs.get('href', None)
            if recipe_name_a else
            None
        )

        recipe['has_page'] = bool(recipe['uri']) and ('new' not in recipe_url_class)

        recipe_image_a = recipe_image_cell.find('a')
        recipe['image_url'] = (
            recipe_image_a.attrs.get('href', None)
            if recipe_image_a else
            None
        )

        materials = recipe.setdefault('materials', [])

        recipe_materials_a = recipe_materials_cell.select('a:not(.image)')
        for material_a in recipe_materials_a:
            material = {}
            materials.append(material)
            material['name'] = material_a.text.strip()
            material['id'] = convert_name_to_id(material['name'])
            material['uri'] = material_a.attrs.get('href', None)

            current_node = material_a
            while current_node and not isinstance(current_node, str):
                current_node = current_node.previous_sibling

            try:
                material['quantity'] = int(re.sub(r'[^\d]', '', current_node))
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

    return recipes


def scrape_raw_materials_from_html_doc(page_contents: str) -> list:
    """
    Converts the crafting_materials.html document to a list of dicts that represent
    that data for those raw materials.
    """
    raw_materials = []
    soup = bs4.BeautifulSoup(page_contents, 'html.parser')
    table_tr_collection = soup.select('.article-table tbody tr')
    for raw_material_tr in table_tr_collection:
        if raw_material_tr.select('th'):
            continue

        raw_material = {}
        raw_materials.append(raw_material)

        cells = raw_material_tr.select('td')

        name_cell = cells[0]
        image_cell = cells[1]
        source_cell = cells[2]
        sell_price_cell = cells[3]

        material_name = name_cell.text.strip()
        raw_material['name'] = material_name
        raw_material['id'] = convert_name_to_id(material_name)

        name_a = name_cell.find('a')

        # Will be used to determine if the recipe has a valid URL (<a> will have a
        # "class" of "new")
        url_class = (
            name_a.attrs.get('class', [])
            if name_a else
            []
        )

        raw_material['uri'] = (
            name_a.attrs.get('href', None)
            if name_a else
            None
        )

        raw_material['has_page'] = bool(raw_material['uri']) and ('new' not in url_class)

        image_a = image_cell.find('a')

        raw_material['image_url'] = (
            image_a.attrs.get('href', None)
            if image_a else
            None
        )

        raw_material['source'] = source_cell.text.strip()

        sell_price = sell_price_cell.text.strip()
        try:
            raw_material['sell_price'] = int(re.sub(r'[^\d]', '', sell_price))
        except:
            raw_material['sell_price'] = None

    return raw_materials


def generate_recipe_table_from_recipe_list(recipes: list) -> dict:
    """
    Converts the list of recipes to dict of recipes that uses each recipe's
    calculated "recipe_id" as the key.
    """

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
                duplicate_recipe['uri'] = recipe['uri']
            elif duplicate_recipe['has_page'] and recipe['has_page']:
                _reconcile_property('uri')

        else:
            recipe_id_map[recipe['id']] = recipe
    
    return recipe_id_map


def calculate_generated_recipe_properties(recipes: dict) -> dict:
    """
    Performs in-place operations on the recipes table, modifying and returning
    the input recipes dict, generating properties that hold calculated fields,
    including:

    - A list of the total raw materials required by the recipe.
    - The total number of crafting steps required for each recipe.
    - A list of the recipes that each recipe depends on, which includes each
      recipe itself.
    """
    adjusted_recipes = set()
    def adjust_recipe(recipe: dict):
        """
        Recursive method that applies the generated properties to the input
        recipe as well as the recipes that it depends on.
        """

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
                    'uri': material['uri'],
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

        recipe['depends_on'] = sorted(list(recipe['depends_on']))

    for _, recipe in recipes.items():
        adjust_recipe(recipe)

    return recipes


def generate_raw_materials_table(recipes: dict, raw_materials: list) -> dict:
    """
    Generates a new table of raw materials to supplement and unpack the raw
    materials used across all recipes.
    """

    raw_materials = {
        raw_material['id']: {
            'name': raw_material['name'],
            'id': raw_material['id'],
            'uri': raw_material['uri'],
            'image_url': raw_material['image_url'],
            'used_in': [],
            'sell_price': raw_material['sell_price']
        }
        for raw_material in
        raw_materials
    }

    for recipe in recipes.values():
        for raw_material_id, raw_material in recipe['raw_materials'].items():
            duplicate_raw_material = raw_materials.get(raw_material_id, None)

            def _reconcile_property(property_name):
                p1 = raw_material.get(property_name, None)
                p2 = duplicate_raw_material.get(property_name, None)
                if p1 and p2 and p1 != p2:
                    print(f"WARNING: Duplicate raw material names with differing {property_name}: Recipe \"{recipe['name']}\" Raw Material: \"{raw_material['name']}\"")
                    raw_material[property_name] = p2

                if (not p2) and p1:
                    duplicate_raw_material[property_name] = p1

                if (not p1) and p2:
                    raw_material[property_name] = p2

            if duplicate_raw_material:
                _reconcile_property('uri')
                duplicate_raw_material['used_in'].append(recipe['id'])

            else:
                raw_materials[raw_material_id] = {
                    'name': raw_material['name'],
                    'id': raw_material['id'],
                    'uri': raw_material['uri'],
                    'image_url': None,
                    'used_in': [recipe['id']],
                    'sell_price': (
                        1 if raw_material['id'] == 'bells' else
                        None
                    ),
                }

    for raw_material in raw_materials.values():
        raw_material['used_in'] = sorted(raw_material['used_in'])

    return raw_materials


def calculate_value_of_raw_materials(recipes: dict, raw_materials: dict):
    """
    Calculates the value of the raw materials that comprise each recipe if the
    player were to sell the raw materials instead of crafting the recipe and
    selling the result.
    """

    def _calculate_value_of_raw_materials(recipe: dict) -> int:
        value_of_raw = 0
        for rm_id, rm_ref in recipe['raw_materials'].items():
            raw_material = raw_materials[rm_id]
            if raw_material['sell_price'] is None:
                return None
            value_of_raw += (rm_ref['quantity'] * raw_material['sell_price'])
        return value_of_raw

    for recipe in recipes.values():
        recipe['value_of_raw_materials'] = _calculate_value_of_raw_materials(recipe)


if __name__ == '__main__':
    recipes = []

    for URL in WIKI_PAGES_DIY_RECIPES:
        recipes_html_contents = load_html_page(URL)
        recipes += scrape_recipes_from_html_doc(recipes_html_contents)

    recipes = generate_recipe_table_from_recipe_list(recipes)

    calculate_generated_recipe_properties(recipes)

    crafting_materials_html_contents = load_html_page(WIKI_PAGE_CRAFTING_MATERIALS)
    raw_materials = scrape_raw_materials_from_html_doc(crafting_materials_html_contents)
    raw_materials = generate_raw_materials_table(recipes, raw_materials)

    calculate_value_of_raw_materials(recipes, raw_materials)

    data = {
        'wiki_base_url': WIKI_BASE_URL,
        'utc_datetime': str(datetime.datetime.now(tz=datetime.timezone.utc)),
        'recipes': recipes,
        'raw_materials': raw_materials,
    }

    with open(os.path.join(FILE_LOCATION, 'diy_recipes.json'), 'w') as recipe_json:
        json.dump(data, recipe_json, indent=2)
