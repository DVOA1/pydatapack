import json
import os
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

logger = logging.getLogger(__name__)  # Create a logger object

# Load version pack format and original files from JSON files
with open(os.path.join(os.getcwd(), "pydatapack", "ver_pack_format.json") , "r") as vpf: ver_pack_format = json.load(vpf)
with open(os.path.join(os.getcwd(), "pydatapack", "original_files.json") , "r") as vpf: original_files = json.load(vpf)

def make_dir(path):
    # Create a directory if it doesn't exist
    try: os.mkdir(path)
    except FileExistsError: return

def version_to_pack(version: str):
    # Convert version string to pack format
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
        # Initialize Recipe class
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

    def __get_count(self, output:str|dict):
        # Get count from output
        if isinstance(output, dict):
            count = output["count"]
            output = output["id"]
        else: count = 1
        return output, count

    def shaped(self, output:str|dict, pattern:list|tuple, inputs:dict):
        # Create a shaped recipe
        output, count = self.__get_count(output)
        self.__new_recipe_folder()
        data = {"type":"minecraft:crafting_shaped","pattern":pattern, "key":inputs, "result":{"id":output, "count":count}}
        self.files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}

    def shapeless(self, output:str|dict, inputs:list|tuple):
        # Create a shapeless recipe
        output, count = self.__get_count(output)
        self.__new_recipe_folder()
        if len(inputs) > 9: raise ValueError("The maximum amount of inputs is 9")
        data = {"type":"minecraft:crafting_shapeless", "ingredients":inputs, "result":{"id":output, "count":count}}
        self.files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}
    
    def __smelting(self, output:str|dict, input:str|dict, xp:float, cookingtime:int, recipe_type:str):
        # Create a smelting recipe
        output, count = self.__get_count(output)
        if isinstance(input, dict): input = input["id"]
        self.__new_recipe_folder()
        data = {"type":recipe_type,"ingredient":{"item":input},"result":{"item":output,"count":count},"experience":xp,"cookingtime":cookingtime}
        self.files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}

    def smelting(self, output:str|dict, input:str|dict, xp:float, cookingtime:int): 
        # Create a smelting recipe
        self.__smelting(output, input, xp, cookingtime, "minecraft:smelting")

    def blasting(self, output:str|dict, input:str|dict, xp:float, cookingtime:int): 
        # Create a blasting recipe
        self.__smelting(output, input, xp, cookingtime, "minecraft:blasting")

    def smoking(self, output:str|dict, input:str|dict, xp:float, cookingtime:int): 
        # Create a smoking recipe
        self.__smelting(output, input, xp, cookingtime, "minecraft:smoking")

    def campfire_cooking(self, output:str|dict, input:str|dict, xp:float, cookingtime:int): 
        # Create a campfire cooking recipe
        self.__smelting(output, input, xp, cookingtime, "minecraft:campfire_cooking")

    def stonecutting(self, output:str|dict, input:str|dict):
        # Create a stonecutting recipe
        output, count = self.__get_count(output)
        if isinstance(input, dict): input = input["id"]
        self.__new_recipe_folder()
        data = {"type":"minecraft:stonecutting","ingredient":input,"result":output,"count":count}
        self.files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}
    
    def smithing(self, base:str|dict, addition:str|dict, output:str|dict):
        # Create a smithing recipe
        if isinstance(base, dict): base = base["id"]
        if isinstance(addition, dict): addition = addition["id"]
        output, count = self.__get_count(output)
        self.__new_recipe_folder()
        data = {"type":"minecraft:smithing","base":base,"addition":addition,"result":{"item":output,"count":count}}
        self.files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}

    def remove(self, output: str):
        # Remove a recipe
        namespace, itemid = output.split(':')
        if self.verbose: logger.info(f"The recipe in namespace {namespace} of {itemid} has been removed")
        self.filters["block"] = [{"namespace":namespace,"path":f"recipe/{itemid}.json"}]
        if self.verbose: logger.info("Calling gen_new")
        self.dtpk.gen_new()

class Elixirum:
    def __init__(self, dtpk):
        # Initialize Elixirum class
        self.dtpk = dtpk
        self.__version__ = "0.2.2"
        self.__all_tags = []
        self.__removed_tags = []
    
    def new_essence(self, effect:str, max_ampl:int, max_dur:int, category:str, min_ingredient: int, min_quality: int):
        # Create a new essence
        category = category.lower()
        if self.dtpk.verbose: logger.info(f"New essence...")
        if category not in ["none", "offensive", "defensive", "enhancing", "diminishing"]: 
            if self.dtpk.verbose: logger.warning(f"Category \"{category}\" is not valid, setting to none")
            category = "none"
        if self.dtpk.verbose: logger.info(f"Creating new essence with effect \"{effect}\", max amplifier {max_ampl}, max duration {max_dur}, category \"{category}\", min ingredient {min_ingredient} and min quality {min_quality}")
        self.dtpk._add_folders(os.path.join("elixirum","elixirum","essence"))
        self.dtpk.files[os.path.join("elixirum","elixirum","essence", f"{effect.split(':')[-1]}.json")] = {"type":"json", "data":{"category":category, "max_amplifier":max_ampl, "max_duration":max_dur, "mob_effect":effect, "required_ingredients":min_ingredient, "required_quality":min_quality}}

    def new_ingredient_preset(self, essence:str|list, ingredient:str, weight:int):
        # Create a new ingredient preset
        self.dtpk._add_folders(os.path.join("elixirum","elixirum","ingredient_preset"))
        essences = {}
        if self.dtpk.verbose: logger.info(f"Creating ingredient preset with essence \"{essence}\" and ingredient \"{ingredient}\" with weight x{weight}")
        if isinstance(essence, list): 
            for ess in essence: essences[ess] = weight
        else: essences[essence] = weight
        self.dtpk.files[os.path.join("elixirum","elixirum","ingredient_preset", f"{ingredient.split(':')[-1]}.json")] = {"type":"json", "data":{"essences": essences,"target": ingredient}}

    def new_configured_elixir(self, data:dict):
        # Create a new configured elixir
        self.dtpk._add_folders(os.path.join("elixirum","elixirum","configured_elixir"))
        self.dtpk.files[os.path.join("elixirum","elixirum","configured_elixir", f"{data['variants'][0][0]['essence'].removeprefix('elixirum:')}.json")] = {"type":"json", "data":data}

    def __add_tag(self, tag:str, tag_type:str, id:str|list, replace:bool=False):
        # Add a tag
        self.dtpk._add_folders(os.path.join("elixirum","tags",tag_type))
        if not isinstance(id, list): self.dtpk.files[os.path.join("elixirum","tags", tag_type, f"{tag}.json")] = {"type":"json", "data":{"replace":replace,"values":[id]}}
        else: self.dtpk.files[os.path.join("elixirum","tags", tag_type, f"{tag}.json")] = {"type":"json", "data":{"replace":replace,"values":id}}
    
    def _confirm_tags(self):
        # Confirm tags
        if not (len(self.__all_tags) > 0): 
            if self.dtpk.verbose: logger.info(f"No tags to confirm")
            return

        if self.dtpk.verbose: logger.info(f"Confirming tags...")

        tags = ["heat_sources", "essence_blacklist", "essence_whitelist", "shelf_placeable"]

        blacklist = original_files["essence_blacklist.json"]["values"]
        for id in self.__removed_tags:
            blacklist.remove(id)
        self.__all_tags.append({"tag":"essence_blacklist", "type":"item", "id":blacklist, "replace":True})
        
        for t in tags:
            tags_id, replace = [], []
            for tag in self.__all_tags:
                if tag["tag"] == t: 
                    if isinstance(tag["id"], list): tags_id.extend(tag["id"])
                    else: tags_id.append(tag["id"])
                    replace.append(tag["replace"])
            if len(tags_id) > 0: 
                if self.dtpk.verbose: logger.info(f"Adding tag \"{t}\" with ids {tags_id} and replace {any(replace)}")
                self.__add_tag(t, tag["type"], tags_id, any(replace))
    
    def __append_tag(self, tag: str, tag_type: str, id: str | list):
        # Append a tag
        if tag == "essence_whitelist":
            ids = id if isinstance(id, list) else [id]
            self.__removed_tags.extend(i for i in ids if i in original_files["essence_blacklist.json"]["values"])
            if self.dtpk.verbose: logger.warning(f"Whitelisted item is in blacklist! Removing {ids} from blacklist")
        if self.dtpk.verbose: logger.info(f"Creating tag \"{tag}\" with type \"{tag_type}\" and id \"{id}\"")
        self.__all_tags.append({"tag": tag, "type": tag_type, "id": id, "replace": False})

    def new_heat_source(self, block: str|list): 
        # Add a new heat source
        self.__append_tag("heat_sources", "block", block)

    def add_to_blacklist(self, item: str|list): 
        # Add an item to the blacklist
        self.__append_tag("essence_blacklist", "item", item)

    def add_to_whitelist(self, item: str|list): 
        # Add an item to the whitelist
        self.__append_tag("essence_whitelist", "item", item)
        
    def make_shelf_placeable(self, item: str|list): 
        # Make an item shelf placeable
        self.__append_tag("shelf_placeable", "item", item)
        
class Datapack:
    def __init__(self, name: str, desc: str, pack_format:str, verbose:bool=False):
        # Initialize Datapack class
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
        # Generate new datapack
        if self.verbose: logger.info("Generating new pack...")
        make_dir(self.basepath)
        if self.verbose: logger.info("Basepath generated")
        with open(os.path.join(self.basepath, "pack.mcmeta"), "w") as mcmeta: json.dump({"pack":{"description":self.desc,"pack_format":self.pack_format}, "filter":self.filters}, mcmeta, indent=4)
        if self.verbose: logger.info("MCMETA generated")
        make_dir(self.datapath)
        if self.verbose: logger.info("Datapath generated")

    def save_data(self, verbose_save:bool|None=None):
        # Save datapack data
        verbose_save = self.verbose if verbose_save == None else verbose_save
        if self.verbose: 
            logger.info(f"{'-'*20} SAVING {'-'*20}")
            logger.info("Saving datapack...")

        if self.verbose: logger.info("Confirming elixirum tags...")
        self.elixirum._confirm_tags()

        if verbose_save: logger.info(f"{'-'*20} FILES AND FOLDERS {'-'*20}")
        
        if len(self.folders) == 0:
            if verbose_save: logger.info("No folders to generate! Returning...")
            return

        for folder in self.folders:
            if verbose_save: logger.info(f"New folder: {os.path.join(self.datapath,folder)}")
            make_dir(os.path.join(self.datapath,folder))

        if len(self.files) == 0: 
            if verbose_save: logger.info("No files to generate! Returning...")
            return
        
        for file in self.files:
            if verbose_save: logger.info(f"New file: {file}")
            with open(os.path.join(self.datapath, file), "w") as fl:
                if self.files[file]["type"] == "json": json.dump(self.files[file]["data"], fl, indent=4)
                else: fl.write(self.files[file]["data"])

        if self.verbose: logger.info("End of save")
    
    def def_load(self, data: str|None = None):
        # Define load function
        if self.verbose: logger.info("Defining all paths to load function")
        self._add_folders(os.path.join("minecraft","tags","functions"))

        if self.verbose: logger.info("Minecraft namespace paths created")
        self._add_folders(os.path.join(self.namespace, "functions"))
        self.files[os.path.join("minecraft", "tags", "functions", "load.json")] = {"type":"json", "data":{"values":[f"{self.namespace}:load"]}}

        if data == None: self.files[os.path.join(self.namespace, "functions", "load.mcfunction")] = {"type":"text", "data":'tellraw @a {"text":"The '+self.name+' datapack has loaded correctly", "color":"green"}'}
        else: self.files[os.path.join(self.namespace, "functions", "load.mcfunction")] = {"type":"text", "data":data}

        if self.verbose: logger.info("All files created")

    def def_tick(self, data: str|None = None):
        # Define tick function
        if self.verbose: logger.info("Defining all paths to tick function")
        self._add_folders(os.path.join("minecraft","tags","functions"))

        if self.verbose: logger.info("Minecraft namespace paths created")
        self._add_folders(os.path.join(self.namespace, "functions"))
        self.files[os.path.join("minecraft","tags","functions","tick.json")] = {"type":"json", "data":{"values":[f"{self.namespace}:tick"]}}

        if data == None: self.files[os.path.join(self.namespace, "functions", "tick.mcfunction")] = {"type":"text", "data":'tellraw @a "Tick!"'}
        else: self.files[os.path.join(self.namespace, "functions", "tick.mcfunction")] = {"type":"text", "data":data}

        if self.verbose: logger.info("All files created")

    def def_func(self, name:str, data:str|None):
        # Define a new function
        if self.verbose: logger.info(f"Defining new \"{name}\" function")

        if os.path.join(self.namespace, "functions") not in self.folders: 
            if self.verbose: logger.info(f"{self.namespace} namespace paths created")
            self._add_folder(os.path.join(self.namespace, "functions"))

        if data == None: self.files[os.path.join(self.namespace, "functions", f"{name}.mcfunction")] = {"type":"text", "data":'tellraw @a {"text":"This function has no data inside", "color":"red"}'}
        else: self.files[os.path.join(self.namespace, "functions", f"{name}.mcfunction")] = {"type":"text", "data":data}