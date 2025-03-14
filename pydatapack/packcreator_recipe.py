import os
from pydatapack.packcreator import logger

class Recipe:
    def __init__(self, dtpk, namespace, _files, __folders, __filters, verbose):
        # Initialize Recipe class
        self.dtpk = dtpk
        self.namespace = namespace
        self._files = _files
        self.__folders = __folders
        self.__filters = __filters
        self.verbose = verbose
        self.dir_made = False

    def __new_recipe_folder(self):
        if self.dir_made: return
        self.__folders.append(os.path.join(self.namespace, "recipe"))
        self.dir_made = True

    def __get_count(self, output:str|dict):
        # Get count from output
        if isinstance(output, dict):
            count = output["count"]
            output = output["id"]
        else: count = 1
        return output, count

    def __check_category(self, category:str, type:int):
        # Check if category is valid
        match type:
            case 0: categories = ["building", "redstone", "equipment", "misc"]
            case 1: categories = ["food", "block", "misc"]
        if category not in categories:
            if self.verbose: logger.warning(f"Category \"{category}\" is not valid, setting to misc")
            return "misc"

    def shaped(self, output:str|dict, pattern:list|tuple, inputs:dict, category:str|None=None):
        # Create a shaped recipe
        output, count = self.__get_count(output)
        self.__check_category(category, 0)
        self.__new_recipe_folder()
        data = {"type":"minecraft:crafting_shaped","category": category, "pattern":pattern, "key":inputs, "result":{"id":output, "count":count}}
        self._files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}

    def shapeless(self, output:str|dict, inputs:list|tuple, category:str|None=None):
        # Create a shapeless recipe
        output, count = self.__get_count(output)
        self.__check_category(category, 0)
        self.__new_recipe_folder()
        if len(inputs) > 9: raise ValueError("The maximum amount of inputs is 9")
        data = {"type":"minecraft:crafting_shapeless", "category": category, "ingredients":inputs, "result":{"id":output, "count":count}}
        self._files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}
    
    def __smelting(self, output:str|dict, input:str|dict, xp:float, cookingtime:int, recipe_type:str, category:str|None=None):
        # Create a smelting recipe
        output, count = self.__get_count(output)
        if isinstance(input, dict): input = input["id"]
        self.__check_category(category, 1)
        self.__new_recipe_folder()
        data = {"type":recipe_type, "category": category, "ingredient":{"item":input},"result":{"item":output,"count":count},"experience":xp,"cookingtime":cookingtime}
        self._files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}

    def smelting(self, output:str|dict, input:str|dict, xp:float, cookingtime:int, category:str|None=None): 
        # Create a smelting recipe
        self.__smelting(output, input, xp, cookingtime, "minecraft:smelting", category)

    def blasting(self, output:str|dict, input:str|dict, xp:float, cookingtime:int, category:str|None=None): 
        # Create a blasting recipe
        self.__smelting(output, input, xp, cookingtime, "minecraft:blasting", category)

    def smoking(self, output:str|dict, input:str|dict, xp:float, cookingtime:int, category:str|None=None): 
        # Create a smoking recipe
        self.__smelting(output, input, xp, cookingtime, "minecraft:smoking", category)

    def campfire_cooking(self, output:str|dict, input:str|dict, xp:float, cookingtime:int, category:str|None=None): 
        # Create a campfire cooking recipe
        self.__smelting(output, input, xp, cookingtime, "minecraft:campfire_cooking", category)

    def stonecutting(self, output:str|dict, input:str|dict):
        # Create a stonecutting recipe
        output, count = self.__get_count(output)
        if isinstance(input, dict): input = input["id"]
        self.__new_recipe_folder()
        data = {"type":"minecraft:stonecutting","ingredient":input,"result":output,"count":count}
        self._files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}
    
    def smithing(self, base:str|dict, addition:str|dict, output:str|dict):
        # Create a smithing recipe
        if isinstance(base, dict): base = base["id"]
        if isinstance(addition, dict): addition = addition["id"]
        output, count = self.__get_count(output)
        self.__new_recipe_folder()
        data = {"type":"minecraft:smithing","base":base,"addition":addition,"result":{"item":output,"count":count}}
        self._files[os.path.join(self.namespace, "recipe", f"{''.join(output.split(':')[-1])}.json")] = {"type":"json", "data":data}

    def remove(self, output: str):
        # Remove a recipe
        namespace, itemid = output.split(':')
        if self.verbose: logger.info(f"The recipe in namespace {namespace} of {itemid} has been removed")
        self.__filters["block"] = [{"namespace":namespace,"path":f"recipe/{itemid}.json"}]
        if self.verbose: logger.info("Calling gen_new")
        self.dtpk.gen_new()