import pydatapack as pdp

test = pdp.Datapack("Time Sayer", "Displays a day number when every day starts", pdp.versionToPack("1.20.1"), True)
test.def_load("""
scoreboard objectives add timesayer dummy
scoreboard players add currtime timesayer 0
scoreboard players add displaytime timesayer 100
scoreboard players add currday timesayer 0
tellraw @a "Time Sayer loaded correctly"
""")
test.def_tick("""
execute store result score currtime timesayer run time query daytime
execute if score currtime timesayer = displaytime timesayer run title @a title ["",{"text":"Day: "},{"score":{"name":"currday","objective":"timesayer"}}]
execute store result score currday timesayer run time query day
""")
test.save_data()