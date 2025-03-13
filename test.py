import pydatapack as pdp

test = pdp.Datapack("TestElixirum", "TEst for ars elixirum", pdp.version_to_pack("1.21.1"), True)

test.def_load()

test.elixirum.new_essence("farmersdelight:comfort", 3, 1200, "enhancing", 1, 1)

test.elixirum.new_ingredient_preset("elixirum:comfort", "create:experience_nugget", 20)

test.elixirum.add_to_blacklist("minecraft:redstone")

test.elixirum.add_to_whitelist("minecraft:water_bucket")

test.save_data()