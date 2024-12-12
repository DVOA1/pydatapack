import pydatapack as pdp

test = pdp.Datapack("TestData", "Questo è un test", pdp.versionToPack("1.20.1"), True)
test.def_load()
test.def_tick()
test.def_func("wassup")
test.recipes.remove("minecraft:iron_ingot")
test.save_data()