import os
import json
from typing import List

import flask
import graphene
import flask_graphql

import backend.models as models

__dir__ = os.path.dirname(__file__)


RECIPE_DATA_FILENAME = os.path.join(__dir__, 'data', 'diy_recipes.json')
with open(RECIPE_DATA_FILENAME) as rdfile:
    RECIPE_DATA = json.load(rdfile)


RECIPES = RECIPE_DATA['recipes']
RAW_MATERIALS = RECIPE_DATA['raw_materials']
WIKI_BASE_URL = RECIPE_DATA['wiki_base_url']


class Query(graphene.ObjectType):
    wiki_base_url = graphene.Field(
        graphene.String,
        resolver=lambda self,info: WIKI_BASE_URL,
        description="Returns the base URL for the Animal Crossing Fandom Wiki.",
    )

    raw_material = graphene.Field(
        models.RawMaterial,
        id=graphene.String(),
        description="Returns a single raw material, using the raw material's ID.",
    )

    def resolve_raw_material(self, info, id):
        return models.get_raw_material(RAW_MATERIALS, id)

    raw_materials = graphene.Field(
        graphene.List(models.RawMaterial),
        description="Returns a list of all raw materials.",
    )

    def resolve_raw_materials(self, info):
        return [
            models.convert_raw_material(rm)
            for rm in
            RAW_MATERIALS.values()
        ]

    recipe = graphene.Field(
        models.Recipe,
        id=graphene.String(),
        description="Returns a single recipe using the recipe's ID.",
    )

    def resolve_recipe(self, info, id):
        return models.get_recipe(RECIPES, RAW_MATERIALS, id)

    recipes = graphene.Field(
        graphene.List(models.Recipe),
        raw_material_id=graphene.String(description="A raw material ID, used to filter the results list to only include recipes that use the specified raw material."),
        recipe_ids=graphene.List(graphene.String, description="A list of recipe IDs, used to filter the list of results."),
        description="Returns a list of recipes. Has a few filter options.",
    )

    def resolve_recipes(self, info, recipe_ids: list=None, raw_material_id: str=None):
        if isinstance(recipe_ids, list):
            recipe_subset_generator = (RECIPES[_id] for _id in recipe_ids)
        else:
            recipe_subset_generator = (recipe for recipe in RECIPES.values())

        if raw_material_id:
            recipe_subset_generator = (
                recipe for recipe in recipe_subset_generator
                if raw_material_id in recipe['raw_materials']
            )

        return [
            models.convert_recipe(RAW_MATERIALS, recipe)
            for recipe in
            recipe_subset_generator
        ]

    class CraftableRecipeRawMaterialArg(graphene.InputObjectType):
        raw_material_id = graphene.String()
        quantity = graphene.Int()

    class CraftableRecipeResponse(graphene.ObjectType):
        recipe = graphene.Field(models.Recipe)
        quantity = graphene.Int()

        total_sell_price = graphene.Int()
        def resolve_total_sell_price(self, info):
            if self.quantity is None or self.recipe.sell_price is None:
                return None

            return self.quantity * self.recipe.sell_price

        total_crafting_steps = graphene.Int()
        def resolve_total_crafting_steps(self, info):
            if self.quantity is None or self.recipe.total_crafting_steps is None:
                return None

            return self.quantity * self.recipe.total_crafting_steps


    craftable_recipes = graphene.Field(
        graphene.List(CraftableRecipeResponse),
        raw_materials=graphene.List(CraftableRecipeRawMaterialArg),
        description="Returns a list of recipes that can be crafted based on a list of raw materials.",
    )

    def resolve_craftable_recipes(self, info, raw_materials: List[CraftableRecipeRawMaterialArg]):
        raw_material_quantities = {
            rm.raw_material_id: rm.quantity
            for rm in
            raw_materials
        }

        craftable_recipes = {}
        for recipe_id, recipe in RECIPES.items():
            min_craftable_quantity = None
            for raw_material_id, raw_material in recipe['raw_materials'].items():
                quantity_required = raw_material['quantity']
                quantity_on_hand = raw_material_quantities.get(raw_material_id, 0)
                craftable_quantity = int(quantity_on_hand / quantity_required)
                min_craftable_quantity = (
                    craftable_quantity if min_craftable_quantity is None else
                    min(min_craftable_quantity, craftable_quantity)
                )

            if min_craftable_quantity:
                craftable_recipes[recipe_id] = min_craftable_quantity

        return [
            Query.CraftableRecipeResponse(
                quantity=craftable_quantity,
                recipe=models.get_recipe(RECIPES, RAW_MATERIALS, recipe_id),
            )
            for recipe_id, craftable_quantity in
            craftable_recipes.items()
        ]


schema = graphene.Schema(query=Query)

app = flask.Flask(__name__)
app.add_url_rule(
    '/',
    view_func=flask_graphql.GraphQLView.as_view(
        '',
        schema=schema,
        graphiql=False
    )
)

app.add_url_rule(
    '/graphiql',
    view_func=flask_graphql.GraphQLView.as_view(
        'graphiql',
        schema=schema,
        graphiql=True
    )
)

if __name__ == '__main__':
    app.run(debug=True)
