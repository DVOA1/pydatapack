import pydatapack as pdp

test = pdp.Datapack("TestElixirum", "TEst for ars elixirum", 48, True)

test.def_load()

test.elixirum.new_essence("farmersdelight:comfort", 3, 1200, "enhancing", 1, 1)

test.elixirum.new_ingredient_preset("elixirum:comfort", "create:experience_nugget", 20)

test.elixirum.new_heat_source("create:blaze_burner")

test.save_data()