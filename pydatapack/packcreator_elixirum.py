import os
import json

from pydatapack.packcreator import logger, cwd

# Load original_files from JSON file
with open(os.path.join(cwd, "pydatapack", "original_files.json") , "r") as vpf: original_files = json.load(vpf)

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
        self.dtpk._files[os.path.join("elixirum","elixirum","essence", f"{effect.split(':')[-1]}.json")] = {"type":"json", "data":{"category":category, "max_amplifier":max_ampl, "max_duration":max_dur, "mob_effect":effect, "required_ingredients":min_ingredient, "required_quality":min_quality}}

    def new_ingredient_preset(self, essence:str|list, ingredient:str, weight:int):
        # Create a new ingredient preset
        self.dtpk._add_folders(os.path.join("elixirum","elixirum","ingredient_preset"))
        essences = {}
        if self.dtpk.verbose: logger.info(f"Creating ingredient preset with essence \"{essence}\" and ingredient \"{ingredient}\" with weight x{weight}")
        if isinstance(essence, list): 
            for ess in essence: essences[ess] = weight
        else: essences[essence] = weight
        self.dtpk._files[os.path.join("elixirum","elixirum","ingredient_preset", f"{ingredient.split(':')[-1]}.json")] = {"type":"json", "data":{"essences": essences,"target": ingredient}}

    def new_configured_elixir(self, data:dict):
        # Create a new configured elixir
        self.dtpk._add_folders(os.path.join("elixirum","elixirum","configured_elixir"))
        self.dtpk._files[os.path.join("elixirum","elixirum","configured_elixir", f"{data['variants'][0][0]['essence'].removeprefix('elixirum:')}.json")] = {"type":"json", "data":data}

    def __add_tag(self, tag:str, tag_type:str, id:str|list, replace:bool=False):
        # Add a tag
        self.dtpk._add_folders(os.path.join("elixirum","tags",tag_type))
        if not isinstance(id, list): self.dtpk._files[os.path.join("elixirum","tags", tag_type, f"{tag}.json")] = {"type":"json", "data":{"replace":replace,"values":[id]}}
        else: self.dtpk._files[os.path.join("elixirum","tags", tag_type, f"{tag}.json")] = {"type":"json", "data":{"replace":replace,"values":id}}
    
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
        