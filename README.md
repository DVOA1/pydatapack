# How to make a datapack for Ars Elixirum

To start you make a "elixirum" folder, referencing the mod. Inside you create another "elixirum" folder, which will contain everything we will make.

## Folders structure

```bash
.
└── data/
    └── elixirum/
        └── elixirum/
            ├── configured_elixir
            ├── elixir_prefix
            ├── essence
            └── ingredient_preset
```

## Configured Elixir folder

Contains an effect (referencing to a pre-made essence) that can have multiple variants.
You can only modify *amplifier* and *duration*

The file name must be the essence name.

Template (taken from the mod code):

```json
{
  "variants": [
    [
      {
        "amplifier": 0,
        "duration": 60,
        "essence": "elixirum:health_boost"
      }
    ],
    [
      {
        "amplifier": 2,
        "duration": 180,
        "essence": "elixirum:health_boost"
      }
    ],
    [
      {
        "amplifier": 5,
        "duration": 360,
        "essence": "elixirum:health_boost"
      }
    ]
  ]
}
```

## Elixir Prefix folder

Didn't look far enough to understand specifically what it does, but seems to be a translation thing. You do not need to put anything into this folder.

Template (taken from the mod code):
```json
{
  "key": "effect_prefix.elixirum.absorption_assimilating",
  "source": "minecraft:absorption"
}
```

## Essence folder

The most important folder. In here you will add your effects with the following parameters:

- "category": can be "NONE","OFFENSIVE","DEFENSIVE","ENHANCING","DIMINISHING".

- "max_amplifier": sets the maximum amplifier the essence can have. The essence can have any amplifier below this number.

- "max_duration": sets the maximum duration the essence can have. The essence can have any duration below this number.

- "mob_effect": the ID of the effect you want to generate (e.g. "farmersdelight:comfort")

- "required_ingredients": minimum amount of ingredient to make this essence.

- "required_quality": minimum amount of quality (???) to make this essence.

The file name must be the effect name (without namespace obv).

Template (generated by my code):

```json
{
    "category": "enhancing",
    "max_amplifier": 3,
    "max_duration": 1200,
    "mob_effect": "farmersdelight:comfort",
    "required_ingredients": 1,
    "required_quality": 10
}
```

## Ingredient Preset folder
Contains every ingredient with a set effect. [NOTE: Almost every item in the game will have a randomly generated effect based on the seed].

Parameters:

- "essences": contains every essence that the set item will have
    - ESSENCE_ID (USING "elixirum:" as namespace) : weight
- "target": contains the item id

The file name must be the item name.

Template (taken from the mod code):

```json
{
  "essences": {
    "elixirum:saturation": 20
  },
  "target": "minecraft:blue_orchid"
}
```

# Template pydatapack for Ars Elixirum

```python
import pydatapack as pdp

# Creates a new datapack with the following parameters (NAME, DESC, PACK_FORMAT, VERBOSE_LOG)
test = pdp.Datapack("TestElixirum", "TEst for ars elixirum", 48, True)

# Creates a generic load mcfunction
test.def_load()

# Creates a new essence with the following parameters (EFFECT_ID, MAX_AMPLIFICATION, MAX_DURATION, CATEGORY, MIN_INGREDIENTS, MIN_QUALITY)
test.elixirum.new_essence("farmersdelight:comfort", 3, 1200, "enhancing", 1, 10)

# Creates a new preset ingredient with the following parameters (ESSENCE [can be string or list], INGREDIENT_ID, WEIGHT)
test.elixirum.new_ingredient_preset("elixirum:comfort", "create:experience_nugget", 20)

# Generates the datapack
test.save_data()
```
