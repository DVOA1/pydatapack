import pydatapack as pdp

test = pdp.Datapack("TestElixirum", "TEst for ars elixirum", 48, True)
test.def_load()

test.elixirum.new_essence("farmersdelight:comfort", 3, 1200, "enhancing", 1, 1)

test.elixirum.new_ingredient_preset("farmersdelight:comfort", "create:experience_nugget", 20)

test.save_data()