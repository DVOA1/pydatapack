import json, os
import pydatapack.pdpckerrors as errorrs

with open(os.path.join(os.getcwd(), "pydatapack", "ver_pack_format.json") , "r") as vpf: ver_pack_format = json.load(vpf)

def make_dir(path):
    try: os.mkdir(path)
    except FileExistsError: return

def version_to_pack(version: str):
    version = [v for v in version.split(".") if v != "1"]
    if len(version) == 1: version.append("0")
    major, minor = int(version[0]), int(version[1])
    temp = ver_pack_format.get(str(major))
    if temp and temp["any"]: return temp["val"]
    for condition in temp["conditions"]:
        value = int(condition["val"])
        match condition["type"]:
            case "less": 
                if minor <= value: return condition["ver"]
            case "more": 
                if minor >= value: return condition["ver"]
            case "equal": 
                if minor == value: return condition["ver"]
            case "between": 
                if value[0] <= minor <= value[1]: return condition["ver"]

class Recipe:
    def __init__(self, dtpk, namespace, files, folders, filters, verbose):
        self.dtpk = dtpk
        self.namespace = namespace
        self.files = files
        self.folders = folders
        self.filters = filters
        self.verbose = verbose
        self.dir_made = False

    def __new_recipe_folder(self):
        '''
        ### Creates a new recipe folder

        ! Used internally !

        Does nothing if a recipe function was already previously called
        '''
        if self.dir_made: return
        self.folders.append(os.path.join(self.namespace, "recipe"))
        self.dir_made = True

    def shaped(self, output:str|dict, pattern:list|tuple, inputs:dict):
        if isinstance(output, dict):
            count = output["count"]
            output = output["id"]
        else: count = 1
        self.__new_recipe_folder()
        data = {"type":"minecraft:crafting_shaped","pattern":pattern, "key":inputs, "result":{"id":output, "count":count}}
        self.files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}

    def shapeless(self, output:str|dict, inputs:list|tuple):
        if isinstance(output, dict):
            count = output["count"]
            output = output["id"]
        else: count = 1
        self.__new_recipe_folder()
        if len(inputs) > 9: raise errorrs.RecipeOutOfSlots
        data = {"type":"minecraft:crafting_shapeless", "ingredients":inputs, "result":{"id":output, "count":count}}
        self.files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}

    def remove(self, output: str):
        namespace, itemid = output.split(':')
        if self.verbose: print(f"The recipe in namespace {namespace} of {itemid} has been removed")
        self.filters["block"] = [{"namespace":namespace,"path":f"recipe/{itemid}.json"}]
        if self.verbose: print("Calling gen_new")
        self.dtpk.gen_new()

class Elixirum:
    def __init__(self, dtpk):
        self.dtpk = dtpk
        self.__version__ = "0.2.2"
    
    def new_essence(self, effect:str, max_ampl:int, max_dur:int, category:str, min_ingredient: int, min_quality: int):
        self.dtpk._add_folders(os.path.join("elixirum","elixirum","essence"))
        self.dtpk.files[os.path.join("elixirum","elixirum","essence", f"{effect.split(':')[-1]}.json")] = {"type":"json", "data":{"category":category, "max_amplifier":max_ampl, "max_duration":max_dur, "mob_effect":effect, "required_ingredients":min_ingredient, "required_quality":min_quality}}

    def new_ingredient_preset(self, essence:str|list, ingredient:str, weight:int):
        self.dtpk._add_folders(os.path.join("elixirum","elixirum","ingredient_preset"))
        essences = {}
        if isinstance(essence, list): 
            for ess in essence: essences[ess] = weight
        else: essences[essence] = weight
        self.dtpk.files[os.path.join("elixirum","elixirum","ingredient_preset", f"{ingredient.split(':')[-1]}.json")] = {"type":"json", "data":{"essences": essences,"target": ingredient}}

    def new_configured_elixir(self, data:dict):
        self.dtpk._add_folders(os.path.join("elixirum","elixirum","configured_elixir"))
        self.dtpk.files[os.path.join("elixirum","elixirum","configured_elixir", f"{data['variants'][0][0]['essence'].removeprefix('elixirum:')}.json")] = {"type":"json", "data":data}

    def __add_tag(self, tag:str, tag_type:str, id:str|list):
        self.dtpk._add_folders(os.path.join("elixirum","tags",tag_type))
        if not isinstance(id, list): self.dtpk.files[os.path.join("elixirum","tags", tag_type, f"{tag}.json")] = {"type":"json", "data":{"replace":False,"values":[id]}}
        else: self.dtpk.files[os.path.join("elixirum","tags", tag_type, f"{tag}.json")] = {"type":"json", "data":{"replace":False,"values":id}}
    
    # TODO: Make new tag function stack the tags in the same file

    def new_heat_source(self, block: str|list): self.__add_tag("heat_sources", "block", block)

    def add_to_blacklist(self, item: str|list): self.__add_tag("essence_blacklist", "item", item)

    def add_to_whitelist(self, item: str|list): self.__add_tag("essence_whitelist", "item", item)
        
    def make_shelf_placeable(self, item: str|list): self.__add_tag("shelf_placeable", "item", item)
        
class Datapack:
    def __init__(self, name: str, desc: str, pack_format:str, verbose:bool=False):
        self.verbose = verbose
        self.name = name
        self.namespace = "".join((name.lower()).split())
        self.desc = desc
        self.pack_format = pack_format
        self.basepath = os.path.join(os.getcwd(), name)
        self.datapath = os.path.join(self.basepath,"data")
        self.folders = [self.namespace]
        self.files = {}
        self.filters = {}
        self.gen_new()
        self.recipes = Recipe(self, self.namespace, self.files, self.folders, self.filters, verbose)
        self.elixirum = Elixirum(self)

    def _add_folder(self, name:str):
        '''
        Used internally

        Appends a folder to the folders list\n
        If it exists returns
        '''
        if name in self.folders: return
        self.folders.append(name)

    def _add_folders(self, path:str):
        '''
        Used internally

        Same as _add_folder but for a long *INEXISTENT* path\n
        If it exists returns
        '''
        path = path.split(os.sep)
        complex_path = ""
        for i in range(len(path)):
            complex_path = os.path.join(complex_path, path[i])
            self._add_folder(complex_path)

    def gen_new(self):
        if self.verbose: print("Generating new pack...")
        make_dir(self.basepath)
        if self.verbose: print("Basepath generated")
        with open(os.path.join(self.basepath, "pack.mcmeta"), "w") as mcmeta: json.dump({"pack":{"description":self.desc,"pack_format":self.pack_format}, "filter":self.filters}, mcmeta, indent=4)
        if self.verbose: print("MCMETA generated")
        make_dir(self.datapath)
        if self.verbose: print("Datapath generated")

    def save_data(self):
        if self.verbose: print("Saving datapack...")

        if len(self.folders) == 0:
            if self.verbose: print("No folders to generate! Returning...")
            return
        
        for folder in self.folders:
            if self.verbose: print("New folder: ", os.path.join(self.datapath,folder))
            make_dir(os.path.join(self.datapath,folder))

        if len(self.files) == 0: 
            if self.verbose: print("No files to generate! Returning...")
            return
        
        for file in self.files:
            if self.verbose: print("New file: ", file)
            with open(os.path.join(self.datapath, file), "w") as fl:
                if self.files[file]["type"] == "json": json.dump(self.files[file]["data"], fl, indent=4)
                else: fl.write(self.files[file]["data"])

        if self.verbose: print("End of save")
    
    def def_load(self, data: str|None = None):
        if self.verbose: print("Defining all paths to load function")
        self._add_folders(os.path.join("minecraft","tags","functions"))

        if self.verbose: print("Minecraft namespace paths created")
        self._add_folders(os.path.join(self.namespace, "functions"))
        self.files[os.path.join("minecraft", "tags", "functions", "load.json")] = {"type":"json", "data":{"values":[f"{self.namespace}:load"]}}

        if data == None: self.files[os.path.join(self.namespace, "functions", "load.mcfunction")] = {"type":"text", "data":'tellraw @a {"text":"The '+self.name+' datapack has loaded correctly", "color":"green"}'}
        else: self.files[os.path.join(self.namespace, "functions", "load.mcfunction")] = {"type":"text", "data":data}

        if self.verbose: print("All files created")

    def def_tick(self, data: str|None = None):
        if self.verbose: print("Defining all paths to tick function")
        self._add_folders(os.path.join("minecraft","tags","functions"))

        if self.verbose: print("Minecraft namespace paths created")
        self._add_folders(os.path.join(self.namespace, "functions"))
        self.files[os.path.join("minecraft","tags","functions","tick.json")] = {"type":"json", "data":{"values":[f"{self.namespace}:tick"]}}

        if data == None: self.files[os.path.join(self.namespace, "functions", "tick.mcfunction")] = {"type":"text", "data":'tellraw @a "Tick!"'}
        else: self.files[os.path.join(self.namespace, "functions", "tick.mcfunction")] = {"type":"text", "data":data}

        if self.verbose: print("All files created")

    def def_func(self, name:str, data:str|None):
        if self.verbose: print("Defining new " + name + " function")

        if os.path.join(self.namespace, "functions") not in self.folders: 
            if self.verbose: print(self.namespace+ " namespace paths created")
            self._add_folder(os.path.join(self.namespace, "functions"))

        if data == None: self.files[os.path.join(self.namespace, "functions", f"{name}.mcfunction")] = {"type":"text", "data":'tellraw @a {"text":"This function has no data inside", "color":"red"}'}
        else: self.files[os.path.join(self.namespace, "functions", f"{name}.mcfunction")] = {"type":"text", "data":data}
