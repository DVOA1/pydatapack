import os

from pydatapack.packcreator import logger, essence_blacklist_file

class Tags:
    def __init__(self, dtpk):
        self.dtpk = dtpk
        self._all_tags = []
        self.__tag_names = ["heat_sources", "essence_blacklist", "essence_whitelist", "shelf_placeable"]

    def __add_tag(self, tag:str, tag_type:str, id:str|list, replace:bool=False, namespace:str|None = None):
        # Add a tag
        if namespace: temp_namespace = namespace
        else: temp_namespace = self.dtpk.namespace
        self.dtpk._add_folders(os.path.join(temp_namespace,"tags",tag_type))
        if not isinstance(id, list): self.dtpk._files[os.path.join(temp_namespace,"tags", tag_type, f"{tag}.json")] = {"type":"json", "data":{"replace":replace,"values":[id]}}
        else: self.dtpk._files[os.path.join(temp_namespace,"tags", tag_type, f"{tag}.json")] = {"type":"json", "data":{"replace":replace,"values":id}}

    def _confirm_tags(self):
        # Confirm tags
        if not (len(self._all_tags) > 0): 
            if self.dtpk.verbose: logger.info(f"No tags to confirm")
            return

        if self.dtpk.verbose: logger.info(f"Confirming tags...")

        if len(self.dtpk.elixirum._removed_tags) > 0:
            blacklist = essence_blacklist_file["essence_blacklist.json"]["values"]
            for id in self.dtpk.elixirum._removed_tags:
                blacklist.remove(id)
            self._all_tags.append({"tag":"essence_blacklist", "type":"item", "id":blacklist, "replace":True})
        
        for t in self.__tag_names:
            tags_id, replace = [], []
            for tag in self._all_tags:
                if tag["tag"] == t: 
                    if isinstance(tag["id"], list): tags_id.extend(tag["id"])
                    else: tags_id.append(tag["id"])
                    replace.append(tag["replace"])
            if len(tags_id) > 0: 
                if self.dtpk.verbose: 
                    namespace_info = f" in namespace {tag.get('namespace')}" if tag.get("namespace", None) is not None else ""
                    logger.debug(f"Adding tag \"{t}\" with ids {tags_id} and replace {any(replace)}{namespace_info}")
                self.__add_tag(t, tag["type"], tags_id, any(replace), tag.get("namespace", None))
    
    def new_tag(self, tag: str, tag_type: str, id: str | list):
        # Append a tag
        if tag not in self.__tag_names: self.__tag_names.append(tag)
        if self.dtpk.verbose: logger.info(f"Creating tag \"{tag}\" with type \"{tag_type}\" and id \"{id}\"")
        self._all_tags.append({"tag": tag, "type": tag_type, "id": id, "replace": False})