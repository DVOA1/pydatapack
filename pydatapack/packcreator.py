import json, os
import pydatapack.pdpckerrors as errorrs

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

class Tools:
    def __init__(self, dtpk, namespace, files, folders, filters, verbose):
        self.dtpk = dtpk
        self.namespace = namespace
        self.files = files
        self.folders = folders
        self.filters = filters
        self.verbose = verbose

class Recipe:
    def __init__(self, dtpk, namespace, files, folders, filters, verbose):
        self.dtpk = dtpk
        self.namespace = namespace
        self.files = files
        self.folders = folders
        self.filters = filters
        self.verbose = verbose
        self.dir_made = False

    def _new_recipe_folder(self):
        '''
        ### Creates a new recipe folder

        ! Used internally !

        Does nothing if a recipe function was already previously called
        '''
        if self.dir_made: return
        self.folders.append(f"{self.namespace}\\recipe")
        self.dir_made = True
    
    def shaped(self, output:str|dict, pattern:list|tuple, inputs:dict):
        if type(output) == dict:
            count = output["count"]
            output = output["id"]
        else: count = 1
        self._new_recipe_folder()
        data = {"type":"minecraft:crafting_shaped","pattern":pattern, "key":inputs, "result":{"id":output, "count":count}}
        self.files[f"{self.namespace}\\recipe\\{''.join(output.split(':').pop())}.json"] = {"type":"json", "data":data}

    def shapless(self, output:str|dict, inputs:list|tuple):
        if type(output) == dict:
            count = output["count"]
            output = output["id"]
        else: count = 1
        if len(inputs) > 9: raise errorrs.RecipeOutOfSlots
        self._new_recipe_folder()
        data = {"type":"minecraft:crafting_shapeless", "ingredients":inputs, "result":{"id":output, "count":count}}
        self.files[f"{self.namespace}\\recipe\\{''.join(output.split(':').pop())}.json"] = {"type":"json", "data":data}

    def remove(self, output: str):
        namespace, itemid = output.split(':')
        if self.verbose: print(f"The recipe in namespace {namespace} of {itemid} has been removed")
        self.filters["block"] = [{"namespace":namespace,"path":f"recipe/{itemid}.json"}]
        if self.verbose: print("Calling gen_new")
        self.dtpk.gen_new()

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
        self.filters = {}
        self.gen_new()
        self.recipes = Recipe(self, self.namespace, self.files, self.folders, self.filters, verbose)

    def _add_folder(self, name):
        '''
        Used internally

        Appends a folder to the folders list\n
        If it exists returns
        '''
        if name in self.folders: return
        self.folders.append(name)

    def _add_folders(self, path):
        '''
        Used internally

        Same as _add_folder but for a long *INEXISTENT* path\n
        If it exists returns
        '''
        path = path.split("\\")
        complex_path = ""
        for i in range(len(path)):
            complex_path += path[i]
            self._add_folder(complex_path)
            complex_path += "\\"

    def gen_new(self):
        if self.verbose: print("Generating new pack...")
        makeDir(self.basepath)
        if self.verbose: print("Basepath generated")
        with open(self.basepath+"\\pack.mcmeta", "w") as mcmeta:
            json.dump({"pack":{"description":self.desc,"pack_format":self.pack_format}, "filter":self.filters}, mcmeta, indent=4)
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
    
    def def_load(self, data: str|None):
        if self.verbose: print("Defining all paths to load function")
        self._add_folders("minecraft\\tags\\functions")
        if self.verbose: print("Minecraft namespace paths created")
        self._add_folder(f"{self.namespace}\\functions")
        self.files["minecraft\\tags\\functions\\load.json"] = {"type":"json", "data":{"values":[f"{self.namespace}:load"]}}
        if type(data) == None:
            self.files[f"{self.namespace}\\functions\\load.mcfunction"] = {"type":"text", "data":'tellraw @a {"text":"The '+self.name+' datapack has loaded correctly", "color":"green"}'}
        else:
            self.files[f"{self.namespace}\\functions\\load.mcfunction"] = {"type":"text", "data":data}
        if self.verbose: print("All files created")

    def def_tick(self, data: str|None):
        if self.verbose: print("Defining all paths to tick function")
        self._add_folders("minecraft\\tags\\functions")
        if self.verbose: print("Minecraft namespace paths created")
        self._add_folder(f"{self.namespace}\\functions")
        self.files["minecraft\\tags\\functions\\tick.json"] = {"type":"json", "data":{"values":[f"{self.namespace}:tick"]}}
        if type(data) == None:
            self.files[f"{self.namespace}\\functions\\tick.mcfunction"] = {"type":"text", "data":'tellraw @a "Tick!"'}
        else:
            self.files[f"{self.namespace}\\functions\\tick.mcfunction"] = {"type":"text", "data":data}
        if self.verbose: print("All files created")

    def def_func(self, name:str, data:str|None):
        if self.verbose: print("Defining new " + name + " function")
        if f"{self.namespace}\\functions" not in self.folders: 
            if self.verbose: print(self.namespace+ " namespace paths created")
            self._add_folder(f"{self.namespace}\\functions")
        if type(data) == None:
            self.files[f"{self.namespace}\\functions\\{name}.mcfunction"] = {"type":"text", "data":'tellraw @a {"text":"This function has no data inside", "color":"red"}'}
        else:
            self.files[f"{self.namespace}\\functions\\{name}.mcfunction"] = {"type":"text", "data":data}

