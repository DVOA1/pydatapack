import os
import json

from pydatapack.packcreator import logger, essence_blacklist_file

class Elixirum:
    def __init__(self, dtpk):
        # Initialize Elixirum class
        self.dtpk = dtpk
        self.__version__ = "0.2.2"
        self._removed_tags = []
    
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
    
    def __append_tag(self, tag: str, tag_type: str, id: str | list):
        # Append a tag
        if tag == "essence_whitelist":
            ids = id if isinstance(id, list) else [id]
            self._removed_tags.extend(i for i in ids if i in essence_blacklist_file["essence_blacklist.json"]["values"])
            if self.dtpk.verbose: logger.warning(f"Whitelisted item is in blacklist! Removing {ids} from blacklist")
        

        data = {"tag": tag, "type": tag_type, "id": id, "replace": False, "namespace":"elixirum"}
        if self.dtpk.verbose: 
            logger.info(f"Creating tag \"{tag}\" with type \"{tag_type}\" and id \"{id}\" {data}")
            logger.debug(f"Data is equal to: {data}")
        self.dtpk.tags._all_tags.append(data)

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
        