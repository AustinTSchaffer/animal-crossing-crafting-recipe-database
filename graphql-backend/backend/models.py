import graphene


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
        for raw_material in iter(self.raw_materials):
            if raw_material.quantity and raw_material.sell_price:
                _sum += raw_material.quantity * raw_material.sell_price
            else:
                return None
        return _sum


def get_raw_material(raw_materials: dict, raw_material_id: str) -> RawMaterial:
    """
    Fetches a raw material from the raw materials dictionary based on the
    `raw_material_id` and converts the plain-dict raw material to a
    RawMaterial model.
    """

    raw_material = raw_materials[raw_material_id]
    return convert_raw_material(raw_material)


def convert_raw_material(raw_material: dict) -> RawMaterial:
    """
    Converts a plain-dict raw material to a RawMaterial model.
    """

    return RawMaterial(**raw_material)


def get_recipe(recipes: dict, raw_materials: dict, recipe_id: str) -> Recipe:
    """
    Fetches a recipe from the recipes dictionary based on the recipe_id and
    converts the plain-dict recipe to a Recipe model. Requires the
    raw_materials dictionary.
    """

    recipe = recipes[recipe_id]
    return convert_recipe(raw_materials, recipe)


def convert_recipe(raw_materials: dict, recipe: dict) -> Recipe:
    """
    Converts the plain-dict recipe to a Recipe model. Requires the
    raw_materials dictionary.
    """

    materials = [
        Recipe.MaterialRef(**material)
        for material in recipe['materials']
    ]

    raw_materials = [
        Recipe.RawMaterialRef(
            **raw_materials[raw_material_id],
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
