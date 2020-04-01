import os
import json

import flask
import graphene
import flask_graphql

__dir__ = os.path.dirname(__file__)

RECIPE_DATA_FILENAME = os.path.join(__dir__, 'data', 'diy_recipes.json')

with open(RECIPE_DATA_FILENAME) as rdfile:
    RECIPE_DATA = json.load(rdfile)

class RawMaterial(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    url = graphene.String()
    used_in = graphene.List(graphene.String)

class Recipe(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    has_page = graphene.Boolean()
    url = graphene.String()
    image_url = graphene.String()
    source = graphene.String()
    sell_price = graphene.Int()
    total_crafting_steps = graphene.Int()
    depends_on = graphene.List(graphene.String)

    class MaterialRef(graphene.ObjectType):
        id = graphene.ID()
        name = graphene.String()
        quantity = graphene.Int()
        url = graphene.String()

    materials = graphene.List(MaterialRef)
    raw_materials = graphene.List(MaterialRef)

def get_raw_material(raw_material_id: str) -> RawMaterial:
    raw_material = RECIPE_DATA['raw_materials'].get(raw_material_id, None)
    return RawMaterial(**raw_material)

def get_recipe(recipe_id: str) -> Recipe:
    recipe = RECIPE_DATA['recipes'].get(recipe_id, None)

    materials = [
        Recipe.MaterialRef(**material)
        for material in recipe['materials']
    ]

    raw_materials = [
        Recipe.MaterialRef(**material)
        for material in recipe['raw_materials'].values()
    ]

    return Recipe(**{
        k: (
            materials if k == 'materials' else
            raw_materials if k == 'raw_materials' else
            v
        )
        for k,v in recipe.items()
    })

class Query(graphene.ObjectType):
    raw_material = graphene.Field(RawMaterial, id=graphene.String())
    recipe = graphene.Field(Recipe, id=graphene.String())

    def resolve_raw_material(self, info, id):
        return get_raw_material(id)

    def resolve_recipe(self, info, id):
        return get_recipe(id)

schema = graphene.Schema(query=Query)

app = flask.Flask(__name__)

app.add_url_rule(
    '/',
    view_func=flask_graphql.GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    )
)

app.run(port=5000)
