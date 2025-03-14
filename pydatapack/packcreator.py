import json
import os
import logging

from shutil import make_archive
from tempfile import TemporaryDirectory
from os import PathLike

# Load all addons
from pydatapack.packcreator_recipe import Recipe
from pydatapack.packcreator_elixirum import Elixirum

# Get current working directory
cwd = os.getcwd()

# Set up logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

# Create a logger object
logger = logging.getLogger(__name__) 

# Load version pack format from JSON file
with open(os.path.join(cwd, "pydatapack", "ver_pack_format.json") , "r") as vpf: ver_pack_format = json.load(vpf)

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
        self.save_to_zip = save_to_zip

        if save_to_zip:
            if self.verbose: logger.info("Creating temporary directory")
            self.temp_dir = TemporaryDirectory()
            self.temp_path = self.temp_dir.name
            if self.verbose: logger.info(f"Temporary directory created. Path: {self.temp_path}")
            if self.verbose: logger.info("Changing save path to temporary directory")
            self.__change_save_path(self.temp_path)
        self.gen_new()

        self.recipes = Recipe(self, self.namespace, self._files, self.__folders, self.__filters, verbose)
        self.elixirum = Elixirum(self)
    
    def __change_save_path(self, path:PathLike|str):
        # Change the save path
        self.basepath = path
        self.datapath = os.path.join(self.basepath,"data")

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
        make_dir(self.basepath)
        if self.verbose: logger.info("Basepath generated")
        with open(os.path.join(self.basepath, "pack.mcmeta"), "w") as mcmeta: json.dump({"pack":{"description":self.desc,"pack_format":self.pack_format}, "filter":self.__filters}, mcmeta, indent=4)
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
        
        if len(self.__folders) == 0:
            if verbose_save: logger.info("No __folders to generate! Returning...")
            return

        for folder in self.__folders:
            if verbose_save: logger.info(f"New folder: {os.path.join(self.datapath,folder)}")
            make_dir(os.path.join(self.datapath,folder))

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
    
    def def_load(self, data: str|None = None):
        # Define load function
        if self.verbose: logger.info("Defining all paths to load function")
        self._add_folders(os.path.join("minecraft","tags","functions"))

        if self.verbose: logger.info("Minecraft namespace paths created")
        self._add_folders(os.path.join(self.namespace, "functions"))
        self._files[os.path.join("minecraft", "tags", "functions", "load.json")] = {"type":"json", "data":{"values":[f"{self.namespace}:load"]}}

        if data == None: self._files[os.path.join(self.namespace, "functions", "load.mcfunction")] = {"type":"text", "data":'tellraw @a {"text":"The '+self.name+' datapack has loaded correctly", "color":"green"}'}
        else: self._files[os.path.join(self.namespace, "functions", "load.mcfunction")] = {"type":"text", "data":data}

        if self.verbose: logger.info("All _files created")

    def def_tick(self, data: str|None = None):
        # Define tick function
        if self.verbose: logger.info("Defining all paths to tick function")
        self._add_folders(os.path.join("minecraft","tags","functions"))

        if self.verbose: logger.info("Minecraft namespace paths created")
        self._add_folders(os.path.join(self.namespace, "functions"))
        self._files[os.path.join("minecraft","tags","functions","tick.json")] = {"type":"json", "data":{"values":[f"{self.namespace}:tick"]}}

        if data == None: self._files[os.path.join(self.namespace, "functions", "tick.mcfunction")] = {"type":"text", "data":'tellraw @a "Tick!"'}
        else: self._files[os.path.join(self.namespace, "functions", "tick.mcfunction")] = {"type":"text", "data":data}

        if self.verbose: logger.info("All _files created")

    def def_func(self, name:str, data:str|None):
        # Define a new function
        if self.verbose: logger.info(f"Defining new \"{name}\" function")

        if os.path.join(self.namespace, "functions") not in self.__folders: 
            if self.verbose: logger.info(f"{self.namespace} namespace paths created")
            self._add_folder(os.path.join(self.namespace, "functions"))

        if data == None: self._files[os.path.join(self.namespace, "functions", f"{name}.mcfunction")] = {"type":"text", "data":'tellraw @a {"text":"This function has no data inside", "color":"red"}'}
        else: self._files[os.path.join(self.namespace, "functions", f"{name}.mcfunction")] = {"type":"text", "data":data}