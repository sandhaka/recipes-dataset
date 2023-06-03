import json
import numpy
import pandas as pd


# Dataset schema
class Dish:
    def __init__(
        self,
        _id,
        recipe_id,
        tags,
        country,
        description,
        keywords,
        language,
        name,
        video_url,
        thumbnail_url,
        score,
        protein,
        fat,
        calories,
        sugar,
        carbohydrates,
        fiber,
        cook_time,
        prep_time,
        total_time,
    ):
        self.id = _id
        self.recipe_id = recipe_id
        self.tags = tags
        self.country = country
        self.description = description
        self.keywords = keywords
        self.language = language
        self.name = name
        self.video_url = video_url
        self.thumbnail_url = thumbnail_url
        self.score = score
        self.protein = protein
        self.fat = fat
        self.calories = calories
        self.sugar = sugar
        self.carbohydrates = carbohydrates
        self.fiber = fiber
        self.prep_time = prep_time
        self.cook_time = cook_time
        self.total_time = total_time


class Ingredient:
    def __init__(
        self,
        part,
        name,
        comment,
        primary_quantity,
        primary_unit,
        metric_quantity,
        metric_unit,
    ):
        self.part = part
        self.name = name
        self.comment = comment
        self.primary_quantity = primary_quantity
        self.primary_unit = primary_unit
        self.metric_quantity = metric_quantity
        self.metric_unit = metric_unit


class Recipe:
    def __init__(self, _id, ingredients: list[Ingredient], _instructions):
        super().__init__()
        self.id = _id
        self.ingredients = ingredients
        self.instructions = _instructions


class Tag:
    def __init__(self, _id, name, display_name, _type):
        self.id = _id
        self.name = name
        self.display_name = display_name
        self.type = _type


# Read data
dishes = pd.read_csv("dishes.csv", sep=",", quotechar='"', encoding="latin1")
tags = pd.read_csv("tags.csv", sep=",", encoding="latin1")
with open("ingredient_and_instructions.json", "r") as f:
    recipes = json.load(f)

# Processing
dishes_collection: list[Dish] = []
recipes_collection: list[Recipe] = []
tags_collection: list[Tag] = []

for recipe_key in recipes.keys():
    recipe_ingredients = []
    ingredient_sections = recipes[recipe_key]["ingredient_sections"]
    for ingredient_section in ingredient_sections:
        section_name = ingredient_section["name"]
        for ingredient_record in ingredient_section["ingredients"]:
            ingredient = Ingredient(
                section_name,
                ingredient_record["name"],
                ingredient_record["extra_comment"],
                ingredient_record["primary_unit"]["quantity"],
                ingredient_record["primary_unit"]["display"],
                ingredient_record["metric_unit"]["quantity"] if ingredient_record["metric_unit"] is not None else None,
                ingredient_record["metric_unit"]["display"] if ingredient_record["metric_unit"] is not None else None,
            )
            recipe_ingredients.append(ingredient)
    recipe_instructions = [instruction["display_text"] for instruction in recipes[recipe_key]["instructions"]]
    recipes_collection.append(Recipe(recipe_key, recipe_ingredients, recipe_instructions))


for i in range(len(tags)):
    td = tags.loc[i, ["id", "name", "display_name", "type"]]
    tag = Tag(int(td.id), td["name"], td.display_name, td.type)
    tags_collection.append(tag)

dish_columns = [
    "id_",
    "country",
    "description",
    "keywords",
    "language",
    "name",
    "video_url",
    "thumbnail_url",
    "score",
    "protein",
    "fat",
    "calories",
    "sugar",
    "carbohydrates",
    "fiber",
    "cook_time",
    "prep_time",
    "total_time",
    "slug",
    "tags",
]

for i in range(len(dishes)):
    dd = dishes.loc[i, dish_columns]
    dish = Dish(
        int(dd.id_),
        dd.slug,
        list(map(lambda t: int(t), dd.tags.split(","))),
        dd.country,
        dd.description,
        dd.keywords,
        dd.language,
        dd.name,
        dd.video_url,
        dd.thumbnail_url,
        dd.score,
        dd.protein,
        dd.fat,
        dd.calories,
        dd.sugar,
        dd.carbohydrates,
        dd.fiber,
        dd.cook_time,
        dd.prep_time,
        dd.total_time,
    )
    dishes_collection.append(dish)


# Write
class DictEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, numpy.int64):  # Resolve int64 type from pandas
            return int(o)
        return o.__dict__


with open("out_set/recipes.json", "w") as f:
    json.dump(recipes_collection, f, cls=DictEncoder, indent=4)
with open("out_set/tags.json", "w") as f:
    json.dump(tags_collection, f, cls=DictEncoder, indent=4)
with open("out_set/dishes.json", "w") as f:
    json.dump(dishes_collection, f, cls=DictEncoder, indent=4)
