# Animal Crossing: Crafting Recipe Database

This repository contains a few inter-related applications that process, serve, and display
data related to all of the crafting recipes from the game: **Animal Crossing: New Horizons**.

A big inspiration for this project was and is the
[Stardew Profits](https://thorinair.github.io/Stardew-Profits/) web application, which helps
users figure out which crops to plant in order to maximize profits.


## Web Scraper (`data/app.py`)

This component of the application is a web scraper that uses Selenium to scrape a few pages from
the [Fandom Animal Crossing Wiki](https://animalcrossing.fandom.com/wiki/Animal_Crossing_Wiki)
in order to generate a JSON document that contains all of the information on crafting recipes
and raw materials from the Wiki.


## GraphQL API (`graphql-backend/app.py`)

This component serves the data generated by the web scraper as a GraphQL API, containing the
following endpoints:

- `wikiBaseUrl: String`: Returns the base URL for the Animal Crossing Fandom Wiki.
- `rawMaterial(id: String): RawMaterial`: Returns a single raw material, using the raw material's ID.
- `rawMaterials: [RawMaterial]`: Returns a list of all raw materials.
- `recipe(id: String):` Recipe: Returns a single recipe using the recipe's ID.
- `recipes(rawMaterialId: StringrecipeIds: [String]): [Recipe]`: Returns a list of recipes. Has a few filter options.
- `craftableRecipes(rawMaterials: [CraftableRecipeRawMaterialArg]): [CraftableRecipeResponse]`: Returns a list of recipes that can be crafted based on a list of raw materials.


## Web Interface

The intent of was to also provide a web interface that allowed users to easily answer questions about
all of the crafting recipes that are available in the game. Some of the questions that I had in mind
while playing the game and working on the web scraper and backend API were:

- What are all of the recipes that use iron nuggets? Clay? Hardwood?
- How much are each of those recipes worth?
- I don't have this recipe... where can I get it?
- How many of this recipe can I craft based on what I currently have on hand?
- Are there any recipes that are worth more than others, relative to the materials that each requires?
- What is the maximum profit that I can make from all of the wood, stone, iron, and clay that I have and what do I need to craft to achieve that?

Work on this component of the application has not yet begun. Please let me know if you are interested
in working on the web interface component by opening an issue on this repository or by emailing me at.

> Austin Schaffer
> 
> schaffer.austin.t (at) gmail.com

Part of the reason why work on the web interface was never started was because catching Tarantulas and
playing the Stalk Market are vastly more profitable, relative to the work required. I still believe that
the crafting system in the game is interesting and exploitable, and this application may still be useful
to those who are looking to maximize their profit on the materials that they've acquired over time.


## Analysis

**Caveat:** Nintendo could change the pricing model for **Animal Crossing: New
Horizons** at any time, which could invalidate the results of this analysis
altogether. Also the data that this analysis was based on was effectively
crowd-sourced from the Animal Crossing Fandom Wiki on April 7th, 2020. On that
date, not all of the recipes available in the game were fully documented in the
Wiki and some of the pricing and materials data that was documented in the Wiki
may have been inaccurate.

In general, most of the craftable items in the game have a sell price that is
equal to double the price of all of the raw materials that went into the recipe
put together. Taking the Hearth as an example, the Hearth recipe requires:

- 2 bamboo pieces, worth 80 bells each
- 4 clay, worth 100 bells each
- 5 hardwood, worth 60 bells each
- 5 iron nuggets, worth 375 bells each

If you sold all of these raw materials on their own, you would receive 2735
bells. If you elect to craft those materials into a hearth then sell the hearth,
you would receive 5470 bells.

This formula works across all crafting materials with the exception of 4 recipes
where the sell price of the completed recipe is worth MORE than double the price
of the materials that were used to craft the recipe and 23 recipes where the
sell price is LESS than double the price of the materials.

The following 4 recipes are worth more than double the price of the materials that
were used to craft them.

| Recipe             | Value of Materials | Value of Recipe | VoR / VoM |
| ------------------ | ------------------ | --------------- | --------- |
| Flimsy fishing rod | 25                 | 100             | 4         |
| Flimsy net         | 25                 | 100             | 4         |
| Fish bait          | 60                 | 200             | 3 1/3     |
| Pitfall seed       | 40                 | 140             | 3 1/2     |

The following 23 recipes are worth less than double the price of the materials
that were used to craft them. If you're looking to generate cash, do not craft
these recipes. Also interesting to note is that all of the recipes that use gold
nuggets show up in this list, meaning there's no way to increase the value of a
gold nugget.

| Recipe               | Value of Materials | Value of Recipe | VoR / VoM          |
| -------------------- | ------------------ | --------------- | ------------------ |
| Axe                  | 655                | 625             | 0.9541984732824428 |
| Flimsy shovel        | 300                | 200             | 0.6666666666666666 |
| Shovel               | 675                | 600             | 0.8888888888888888 |
| Fishing rod          | 400                | 600             | 1.5                |
| Net                  | 400                | 600             | 1.5                |
| Flimsy watering can  | 300                | 200             | 0.6666666666666666 |
| Watering can         | 675                | 600             | 0.8888888888888888 |
| Slingshot            | 300                | 225             | 0.75               |
| Golden slingshot     | 10300              | 10300           | 1.0                |
| Birdbath             | 450                | 400             | 0.8888888888888888 |
| Palm-tree lamp       | 2640               | 3280            | 1.2424242424242424 |
| Aroma holder         | 400                | 600             | 1.5                |
| Coconut juice        | 500                | 500             | 1.0                |
| Golden arowana model | 30000              | 30000           | 1.0                |
| Gold bars            | 30000              | 30000           | 1.0                |
| Golden candlestick   | 20000              | 20000           | 1.0                |
| Golden dishes        | 10000              | 10000           | 1.0                |
| Golden dung beetle   | 30000              | 30000           | 1.0                |
| Coconut wall planter | 550                | 600             | 1.0909090909090908 |
| Golden gears         | 11125              | 11125           | 1.0                |
| Gold armor           | 80000              | 80000           | 1.0                |
| Leaf                 | 50                 | 80              | 1.6                |
| Medicine             | 330                | 100             | 0.3030303030303030 |

If you ignore those 27 recipes and gold nuggets, you can generate a table of the
value of each crafting material when used in a crafting recipe by doubling its
sell price.

| Raw Material         | Sell Price When Crafted | Stack Size | Value of a Stack |
| -------------------- | ----------------------- | ---------- | ---------------- |
| Iron nugget          | 750                     | 30         | 22500            |
| Young spring bamboo  | 400                     | 30         | 12000            |
| Earth Egg            | 400                     | 30         | 12000            |
| Stone Egg            | 400                     | 30         | 12000            |
| Leaf Egg             | 400                     | 30         | 12000            |
| Wood Egg             | 400                     | 30         | 12000            |
| Sky Egg              | 400                     | 30         | 12000            |
| Water Egg            | 400                     | 30         | 12000            |
| Coconut              | 1000                    | 10         | 10000            |
| Clay                 | 200                     | 30         | 6000             |
| Wasp nest            | 600                     | 10         | 6000             |
| Stone                | 150                     | 30         | 4500             |
| Bamboo piece         | 160                     | 30         | 4800             |
| Wood                 | 120                     | 30         | 3600             |
| Hardwood             | 120                     | 30         | 3600             |
| Softwood             | 120                     | 30         | 3600             |
| Cherry-blossom petal | 400                     | 10         | 4000             |
| Fruit                | 200 (Regardless)        | 10         | 2000             |
| Clump of weeds       | 20                      | 99         | 1980             |
| Tree branch          | 10                      | 30         | 300              |
| Fossil               | 200                     | 1          | 200              |

From this table, you can see that only stacks of bunny day eggs, coconuts, young
spring bamboo, and iron nuggets are worth more than a single tarantula or
scorpion. I personally would argue that the effort required to get a stack of
any one of those is higher than the effort required to set up a viable tarantula
island and then catch a few. Regardless, this table may still useful when
choosing between a partial stack of wood and the fish that you just caught, or
motivating yourself to turn all of the unused materials in your possession into
a little extra cash.

## Recommendations

Don't just sell all of your resources, craft them into stuff in order to double
their value. ...except gold nugs, those are always worth 10k. Also, just sell
your extra sticks. The crafting recipes that use them really aren't worth the
trouble.

If you REALLY want to make loads o' money, save a little cash and play the Stalk
Market. Just like in America, you don't get rich in Animal Crossing by working.

Most importantly, don't be like me and try to optimize every detail. Just play
the game and have fun.
