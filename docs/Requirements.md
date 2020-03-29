# AC:NH "Crafting for Bells" Calculator

## Initial Requirements

- Should accept a collection of materials with quantities (Omit weeds? Given how
  easy they are to acquire?)
- Should output a list of recipes that the player should craft in order to
  maximize profit.
- Need a database of crafting recipes so that changes to recipes and prices can
  be accounted for. Start with scraping the Wiki page
  (https://animalcrossing.fandom.com/wiki/DIY_recipes) to a JSON doc and go from
  there.
- Loopback/recursion, some recipes depend on the output of other recipes.
  Possibly account for this by making compound recipes in the database,
  increasing the "labor cost" of the recipe.

## V2 Requirements

- An option to say "I can't make this, I don't have this recipe"
- Labor is a resource and the calculator should seek to minimize "number of
  items crafted"
- Which resource should I prioritize?
- Include "null recipes" aka "1 iron = 1 iron (cost X)" aka "just sell the iron
  you idiot"
