import os
import json

import flask
import graphene
import flask_graphql

__dir__ = os.path.dirname(__file__)


RECIPE_DATA_FILENAME = os.path.join(__dir__, 'data', 'diy_recipes.json')
with open(RECIPE_DATA_FILENAME) as rdfile:
    RECIPE_DATA = json.load(rdfile)


RECIPES = RECIPE_DATA['recipes']
RAW_MATERIALS = RECIPE_DATA['raw_materials']
WIKI_BASE_URL = RECIPE_DATA['wiki_base_url']


class RawMaterial(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    uri = graphene.String()
    image_url = graphene.String()
    used_in = graphene.List(graphene.String)
    sell_price = graphene.Int()


class Recipe(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    has_page = graphene.Boolean()
    uri = graphene.String()
    image_url = graphene.String()
    source = graphene.String()
    sell_price = graphene.Int()
    total_crafting_steps = graphene.Int()
    depends_on = graphene.List(graphene.String)

    class MaterialRef(graphene.ObjectType):
        id = graphene.ID()
        name = graphene.String()
        quantity = graphene.Int()
        uri = graphene.String()

    class RawMaterialRef(RawMaterial):
        quantity = graphene.Int()

    materials = graphene.List(MaterialRef)
    raw_materials = graphene.List(RawMaterialRef)

    estimated_sell_price = graphene.Int()
    def resolve_estimated_sell_price(self, info):
        _sum = 0
        for raw_material in self.raw_materials:
            if raw_material.quantity and raw_material.sell_price:
                _sum += raw_material.quantity * raw_material.sell_price
            else:
                return None
        return _sum


def get_raw_material(raw_material_id: str) -> RawMaterial:
    raw_material = RAW_MATERIALS[raw_material_id]
    return RawMaterial(**raw_material)


def get_recipe(recipe_id: str) -> Recipe:
    recipe = RECIPES[recipe_id]

    materials = [
        Recipe.MaterialRef(**material)
        for material in recipe['materials']
    ]

    raw_materials = [
        Recipe.RawMaterialRef(
            **RAW_MATERIALS[raw_material_id],
            quantity=raw_material_ref['quantity'],
        )
        for raw_material_id, raw_material_ref in
        recipe['raw_materials'].items()
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
    wiki_base_url = graphene.Field(graphene.String)
    raw_material = graphene.Field(RawMaterial, id=graphene.String())
    raw_materials = graphene.Field(graphene.List(RawMaterial))
    recipe = graphene.Field(Recipe, id=graphene.String())
    recipes = graphene.Field(graphene.List(Recipe))

    def resolve_wiki_base_url(self, info):
        return WIKI_BASE_URL

    def resolve_raw_material(self, info, id):
        return get_raw_material(id)

    def resolve_raw_materials(self, info):
        return list(map(get_raw_material, RAW_MATERIALS))

    def resolve_recipe(self, info, id):
        return get_recipe(id)

    def resolve_recipes(self, info):
        return list(map(get_recipe, RECIPES))

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
