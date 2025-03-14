### ARS ELIXIRUM DOCS ARE NOW MOVED IN A [NEW REPOSITORY](https://github.com/DVOA1/ElixirumDocs)

![LOGO](assets/logo.png "Pydatapack logo")

## Pydatapack Documentation

### Overview
**Pydatapack** is a Python script designed to facilitate the creation and management of Minecraft datapacks.

### Classes and Methods

#### Datapack

- **`Datapack(self, name: str, desc: str, pack_format: str, verbose: bool = False)`**: Initializes the Datapack class.

- **`save_data(self, verbose_save: bool | None = None)`**: Saves the datapack data and generates all the necessary files and folders.

- **`def_load(self, data: str | None = None)`**: Defines the load function.

- **`def_tick(self, data: str | None = None)`**: Defines the tick function.

- **`def_func(self, name: str, data: str | None)`**: Defines a new function.

#### Recipe

- **`recipe.shaped(self, output: str | dict, pattern: list | tuple, inputs: dict, category: str | None = None)`**: Creates a shaped recipe.

- **`recipe.shapeless(self, output: str | dict, inputs: list | tuple, category: str | None = None)`**: Creates a shapeless recipe.

- **`recipe.smelting(self, output: str | dict, input: str | dict, xp: float, cookingtime: int, category: str | None = None)`**: Creates a smelting recipe.

- **`recipe.blasting(self, output: str | dict, input: str | dict, xp: float, cookingtime: int, category: str | None = None)`**: Creates a blasting recipe.

- **`recipe.smoking(self, output: str | dict, input: str | dict, xp: float, cookingtime: int, category: str | None = None)`**: Creates a smoking recipe.

- **`recipe.campfire_cooking(self, output: str | dict, input: str | dict, xp: float, cookingtime: int, category: str | None = None)`**: Creates a campfire cooking recipe.

- **`recipe.stonecutting(self, output: str | dict, input: str | dict)`**: Creates a stonecutting recipe.

- **`recipe.smithing(self, base: str | dict, addition: str | dict, output: str | dict)`**: Creates a smithing recipe.

- **`recipe.remove(self, output: str)`**: Removes a recipe.

#### Elixirum

> This generator implements all the functionalities for making Ars Elixirum datapacks, including creating new essences, ingredient presets, configured elixirs, adding heat sources, and managing blacklists and whitelists.
For a more detailed explanation on what the parameters do, please consult the [Ars Elixirum documentation](https://github.com/DVOA1/ElixirumDocs/blob/main/README.md#elixirum)

- **`new_essence(self, effect: str, max_ampl: int, max_dur: int, category: str, min_ingredient: int, min_quality: int)`**: Creates a new essence.

- **`new_ingredient_preset(self, essence: str | list, ingredient: str, weight: int)`**: Creates a new ingredient preset.

- **`new_configured_elixir(self, data: dict)`**: Creates a new configured elixir.

- **`new_heat_source(self, block: str | list)`**: Adds a new heat source.

- **`add_to_blacklist(self, item: str | list)`**: Adds an item to the blacklist.

- **`add_to_whitelist(self, item: str | list)`**: Adds an item to the whitelist.

- **`make_shelf_placeable(self, item: str | list)`**: Makes an item shelf placeable.

### Logging

The script uses Python's built-in logging module to provide detailed logs of its operations. Logging is configured at the beginning of the script and can be controlled via the `verbose` parameter in the `Datapack` class.

### Usage

To use the script, create an instance of the `Datapack` class and use its methods to define recipes, tags, and other datapack elements. Save the datapack using the `save_data` method.

Example:

```python
dp = Datapack("MyDatapack", "A custom Minecraft datapack", "6", verbose=True)
dp.recipes.shaped("minecraft:diamond_sword", [" A ", " A ", " B "], {"A": "minecraft:diamond", "B": "minecraft:stick"})
dp.save_data()
```

Ars Elixirum example:

```python
import pydatapack as pdp

# Creates a new datapack
datapack = pdp.Datapack("TestElixirum", "Test for Ars Elixirum", 48, True)

# Creates a generic load mcfunction
datapack.def_load()

# Creates a new comfort essence
datapack.elixirum.new_essence("farmersdelight:comfort", 3, 1200, "enhancing", 1, 10)

# Creates a new ingredient preset
datapack.elixirum.new_ingredient_preset("elixirum:comfort", "create:experience_nugget", 20)

# Adds the '#elixirum:heat_sources' tag to the block
datapack.elixirum.new_heat_source("create:blaze_burner")

# You can also add the following tags with their respective methods:
# - '#elixirum:essences_blacklist' : DATAPACK.elixirum.add_to_blacklist(ITEM)
# - '#elixirum:essences_whitelist' : DATAPACK.elixirum.add_to_whitelist(ITEM)
# - '#elixirum:potion_shelf_placeable' : DATAPACK.elixirum.make_shelf_placeable(ITEM)

# Confirms everything an generates the datapack
datapack.save_data()
```

##### DVOA1 | 2025