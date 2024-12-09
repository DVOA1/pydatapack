import json, os

with open(os.getcwd()+"\\pydatapack\\ver_pack_format.json", "r") as vpf:
    ver_pack_format = json.load(vpf)

def makeDir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        return

def versionToPack(version:str):
    version = version.split(".")
    version.remove("1")
    if len(version) == 1: version.append("0")
    temp = ver_pack_format[version[0]]
    if temp["any"]: return temp["val"]
    else:
        version = [int(i) for i in version]
        for condition in temp["conditions"]:
            if condition["type"] == "less":
                value = int(condition["val"])
                if version[1] <= value: return condition["ver"]
            elif condition["type"] == "more":
                value = int(condition["val"])
                if version[1] >= value: return condition["ver"]
            elif condition["type"] == "equal":
                value = int(condition["val"])
                if version[1] == value: return condition["ver"]
            elif condition["type"] == "between":
                values = [int(condition["val"][0]), int(condition["val"][1])]
                if (version[1] >= values[0]) and (version[1] <= values[1]): return condition["ver"]

class Datapack:
    def __init__(self, name: str, desc: str, pack_format:str, verbose:bool=False):
        self.verbose = verbose
        self.name = name
        self.namespace = "".join((name.lower()).split())
        self.desc = desc
        self.pack_format = pack_format
        self.basepath = os.getcwd()+"\\"+self.name
        self.datapath = self.basepath+"\\data"
        self.folders = [self.namespace]
        self.files = {}
        self.gen_new()

    def gen_new(self):
        if self.verbose: print("Generating new pack...")
        makeDir(self.basepath)
        if self.verbose: print("Basepath generated")
        with open(self.basepath+"\\pack.mcmeta", "w") as mcmeta:
            json.dump({"pack":{"description":self.desc,"pack_format":self.pack_format}}, mcmeta, indent=4)
        if self.verbose: print("MCMETA generated")
        makeDir(self.datapath)
        if self.verbose: print("Datapath generated")

    def save_data(self):
        if self.verbose: print("Saving datapack...")
        if len(self.folders) == 0:
            if self.verbose: print("No folders to generate! Returning...")
            return
        for folder in self.folders:
            if self.verbose: print("New folder: " + folder)
            makeDir(self.datapath+"\\"+folder)
        if len(self.files) == 0: 
            if self.verbose: print("No files to generate! Returning...")
            return
        for file in self.files:
            if self.verbose: print("New file: " + file)
            if self.files[file]["type"] == "json":
                with open(self.datapath+"\\"+file, "w") as fl:
                    json.dump(self.files[file]["data"], fl, indent=4)
            else:
                with open(self.datapath+"\\"+file, "w") as fl:
                    fl.write(self.files[file]["data"])
        if self.verbose: print("End of save")
    
    def def_load(self):
        if self.verbose: print("Defining all paths to load function")
        self.folders.append("minecraft")
        self.folders.append("minecraft\\tags")
        self.folders.append("minecraft\\tags\\functions")
        if self.verbose: print("Minecraft namespace paths created")
        if f"{self.namespace}\\functions" not in self.folders: 
            if self.verbose: print(self.namespace+ " namespace paths created")
            self.folders.append(f"{self.namespace}\\functions")
        self.files["minecraft\\tags\\functions\\load.json"] = {"type":"json", "data":{"values":[f"{self.namespace}:load"]}}
        self.files[f"{self.namespace}\\functions\\load.mcfunction"] = {"type":"text", "data":'tellraw @a {"text":"The '+self.name+' datapack has loaded correctly", "color":"green"}'}
        if self.verbose: print("All files created")

    def def_tick(self):
        if self.verbose: print("Defining all paths to tick function")
        self.folders.append("minecraft")
        self.folders.append("minecraft\\tags")
        self.folders.append("minecraft\\tags\\functions")
        if self.verbose: print("Minecraft namespace paths created")
        if f"{self.namespace}\\functions" not in self.folders: 
            if self.verbose: print(self.namespace+ " namespace paths created")
            self.folders.append(f"{self.namespace}\\functions")
        self.files["minecraft\\tags\\functions\\tick.json"] = {"type":"json", "data":{"values":[f"{self.namespace}:tick"]}}
        self.files[f"{self.namespace}\\functions\\tick.mcfunction"] = {"type":"text", "data":'tellraw @a "Tick!"'}
        if self.verbose: print("All files created")

    def def_func(self, name:str):
        if self.verbose: print("Defining new " + name + " function")
        if f"{self.namespace}\\functions" not in self.folders: 
            if self.verbose: print(self.namespace+ " namespace paths created")
            self.folders.append(f"{self.namespace}\\functions")
        self.files[f"{self.namespace}\\functions\\{name}.mcfunction"] = {"type":"text", "data":'tellraw @a {"text":"This function has no data inside", "color":"red"}'}

