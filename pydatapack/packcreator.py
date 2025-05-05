import json
import os
import logging
import re

from pydatapack.log_formatter import ColorFormatter
from shutil import make_archive
from tempfile import TemporaryDirectory
from os import PathLike

# Get current working directory
cwd = os.getcwd()

logger_level = logging.DEBUG

# Create a logger object
logger = logging.getLogger(__name__)
logger.setLevel(logger_level)

# Create logging stream handler
ch = logging.StreamHandler()
ch.setLevel(logger_level)
ch.setFormatter(ColorFormatter())
logger.addHandler(ch)

# Load version pack format from JSON file
with open(os.path.join(cwd, "pydatapack", "ver_pack_format.json") , "r") as vpf: ver_pack_format = json.load(vpf)
# Load essence_blacklist_file from JSON file
with open(os.path.join(cwd, "pydatapack", "essence_blacklist_file.json") , "r") as vpf: essence_blacklist_file = json.load(vpf)

# Load all addons
from pydatapack.packcreator_recipe import Recipe
from pydatapack.packcreator_elixirum import Elixirum
from pydatapack.packcreator_tags import Tags

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

class Datapack:
    def __init__(self, name: str, desc: str, pack_format:str, save_to_zip:bool=False, verbose:bool=False):
        # Initialize Datapack class
        self.verbose = verbose
        self.name = name
        self.namespace = "".join((name.lower()).split())
        self.desc = desc
        self.pack_format = pack_format

        self.basepath = os.path.join(cwd, name)
        self.datapath = os.path.join(self.basepath,"data")

        self.__folders = [self.namespace]
        self._files = {}
        self.__filters = {}
        self.__all_tags = []
        self.__tags_name = []
        self.save_to_zip = save_to_zip

        if save_to_zip:
            if self.verbose: logger.info("Creating temporary directory")
            self.temp_dir = TemporaryDirectory()
            self.temp_path = self.temp_dir.name
            if self.verbose: logger.info(f"Temporary directory created. Path: {self.temp_path}")
            if self.verbose: logger.info("Changing save path to temporary directory")
            self.__change_save_path(self.temp_path)
        self.gen_new()

        self.tags = Tags(self)
        self.recipes = Recipe(self, self.namespace, self._files, self.__folders, self.__filters, verbose)
        self.elixirum = Elixirum(self)
    
    def __change_save_path(self, path:PathLike|str):
        # Change the save path
        self.basepath = path
        self.datapath = os.path.join(self.basepath,"data")
    
    def __make_dir(self, path: PathLike|str, verbose_save: bool = True):
        # Create a directory if it doesn't exist
        try: os.mkdir(path)
        except FileExistsError: 
            if verbose_save: logger.error(f"Path already exists! Returning...")
            return

    def _add_folder(self, name:str):
        '''
        Used internally

        Appends a folder to the __folders list\n
        If it exists returns
        '''
        if name in self.__folders: return
        self.__folders.append(name)

    def _add_folders(self, path:PathLike|str):
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
        self.__make_dir(self.basepath)
        if self.verbose: logger.info("Basepath generated")
        with open(os.path.join(self.basepath, "pack.mcmeta"), "w") as mcmeta: 
            if len(self.__filters) > 0: json.dump({"pack":{"description":self.desc,"pack_format":self.pack_format}, "filter":self.__filters}, mcmeta, indent=4)
            else: json.dump({"pack":{"description":self.desc,"pack_format":self.pack_format}}, mcmeta, indent=4)
        if self.verbose: logger.info("MCMETA generated")
        self.__make_dir(self.datapath)
        if self.verbose: logger.info("Datapath generated")

    def save_data(self, verbose_save:bool|None=None):
        # Save datapack data
        verbose_save = self.verbose if verbose_save == None else verbose_save
        if self.verbose: 
            logger.info(f"{'-'*20} SAVING {'-'*20}")
            logger.info("Saving datapack...")

        if self.verbose: logger.info("Confirming all tags...")
        self.tags._confirm_tags()

        if verbose_save: 
            logger.info(f"{'-'*20} FILES AND FOLDERS {'-'*20}")
        else: logger.info("Verbose save is turned off")
        
        if len(self.__folders) == 0:
            if verbose_save: logger.info("No folders to generate! Returning...")
            return

        for folder in self.__folders:
            if verbose_save: logger.info(f"New folder: {os.path.join(self.datapath,folder)}")
            self.__make_dir(os.path.join(self.datapath,folder), verbose_save=verbose_save)

        if len(self._files) == 0: 
            if verbose_save: logger.info("No _files to generate! Returning...")
            return
        
        for file in self._files:
            if verbose_save: logger.info(f"New file: {file}")
            with open(os.path.join(self.datapath, file), "w") as fl:
                if self._files[file]["type"] == "json": json.dump(self._files[file]["data"], fl, indent=4)
                else: fl.write(self._files[file]["data"])

        if self.save_to_zip:
            logger.info(f"{'-'*20} CREATING ZIP {'-'*20}")
            if self.verbose: logger.info("Creating zip archive")
            make_archive(self.name, 'zip', self.temp_path, verbose=verbose_save)

            if self.verbose: logger.info("Cleaning up temp directory")
            self.temp_dir.cleanup()

        if self.verbose: logger.info("End of save")
    
    def get_ids_from_pattern(self, pattern: str):
        
        """
        Recursively expand the first parenthesized group of alternatives
        in the pattern, until no more are left.
        """
        m = re.search(r'\(([^()]+)\)', pattern)
        if not m:
            return [pattern]
        
        variants = []
        whole_group = m.group(0)
        inner = m.group(1)
        options = inner.split('|')
        
        for opt in options:
            new_pattern = pattern[:m.start()] + opt + pattern[m.end():]
            variants.extend(self.get_ids_from_pattern(new_pattern))
        
        return variants

    def def_load(self, data: str|None = None):
        # Define load function
        if self.verbose: logger.info("Defining all paths to load function")

        if self.pack_format >= 48: funct_folder = "function"
        else: funct_folder = "functions"

        self._add_folders(os.path.join("minecraft","tags",funct_folder))

        if self.verbose: logger.info("Minecraft namespace paths created")
        self._add_folders(os.path.join(self.namespace, funct_folder))
        self._files[os.path.join("minecraft", "tags", funct_folder, "load.json")] = {"type":"json", "data":{"values":[f"{self.namespace}:load"]}}

        if data == None: self._files[os.path.join(self.namespace, funct_folder, "load.mcfunction")] = {"type":"text", "data":'tellraw @a {"text":"The '+self.name+' datapack has loaded correctly", "color":"green"}'}
        else: self._files[os.path.join(self.namespace, funct_folder, "load.mcfunction")] = {"type":"text", "data":data}

        if self.verbose: logger.info("All _files created")

    def def_tick(self, data: str|None = None):
        # Define tick function
        if self.verbose: logger.info("Defining all paths to tick function")

        if self.pack_format >= 48: funct_folder = "function"
        else: funct_folder = "functions"

        self._add_folders(os.path.join("minecraft","tags",funct_folder))

        if self.verbose: logger.info("Minecraft namespace paths created")
        self._add_folders(os.path.join(self.namespace, funct_folder))
        self._files[os.path.join("minecraft","tags",funct_folder,"tick.json")] = {"type":"json", "data":{"values":[f"{self.namespace}:tick"]}}

        if data == None: self._files[os.path.join(self.namespace, funct_folder, "tick.mcfunction")] = {"type":"text", "data":'tellraw @a "Tick!"'}
        else: self._files[os.path.join(self.namespace, funct_folder, "tick.mcfunction")] = {"type":"text", "data":data}

        if self.verbose: logger.info("All _files created")

    def def_func(self, name:str, data:str|None):
        # Define a new function
        if self.verbose: logger.info(f"Defining new \"{name}\" function")

        if self.pack_format >= 48: funct_folder = "function"
        else: funct_folder = "functions"

        if os.path.join(self.namespace, funct_folder) not in self.__folders: 
            if self.verbose: logger.info(f"{self.namespace} namespace paths created")
            self._add_folder(os.path.join(self.namespace, funct_folder))

        if data == None: self._files[os.path.join(self.namespace, funct_folder, f"{name}.mcfunction")] = {"type":"text", "data":'tellraw @a {"text":"This function has no data inside", "color":"red"}'}
        else: self._files[os.path.join(self.namespace, funct_folder, f"{name}.mcfunction")] = {"type":"text", "data":data}