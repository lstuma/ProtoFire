from typing import Callable
from collections import UserDict
import re
from pigeon.http import error


class ParameterDict(UserDict):
    def __getattr__(self, key):
        return self.data.get(key)


class View:
    def __init__(self, target: str, func: Callable, mimetype: str):
        self.target = target
        self.func = func
        self.mimetype = mimetype
        
    def match(self, path: str) -> bool:
        """
        Check for the requested path matching the views target.
        """

        target = re.sub(r"\{\{(.*?)\}\}", r"[^/]{1,}", self.target)
        pattern = re.compile(target)
        return bool(pattern.match(path))
    
    def __call__(self, request, dynamic_params=None):
        return self.func(request, dynamic_params)

    def get_dynamic(self, path: str) -> ParameterDict:
        """
        Returns dict of dynamic url params.
        """

        target = self.target

        names_list = re.findall(r"\{\{[^\}]{1,}\}\}", target)  # get list of parameter names

        target_ = target

        for name in names_list:
            target_ = target_.replace(name, "\sep")  # add seperator to identify regions between the params

        sep = {i for i in target_.split("\sep") if i}  # create set of regions between the params

        for s in sep:
            target = target.replace(s, "/")  # replace the regions betweeen the params with /
            path = path.replace(s, "/")      # replace the regions betweeen the params with /

        names = {}
        params = ParameterDict()

        for n, i in enumerate(target.split("/")):  # iterate over the params where n is the param-name index and i is the param
            if i.startswith("{{") and i.endswith("}}"):
                names[n] = i.replace("{{", "").replace("}}", "")  # build names dictionary where the index n is the key and the param-name the value

        for n, i in enumerate(path.split("/")):  # iterate over the params where n is the params index and i is the param
            if n in names:  # check if the param really is a param
                params[names[n]] = i  # build ParameterDict where the key is the param-name and the value is the actual param 

        return params  


class ViewHandler:
    def __init__(self):
        self.views: list[View] = []

    def register(self, target, func, mimetype):
        """
        Add new view to ViewHandler instance.
        """
        self.views.append(View(target, func, mimetype))

    def _get_view(self, path: str, mimetype: str) -> View | None:
        """
        returns view object matching path and mimetype.
        """
        for view in self.views:
            if view.match(path):
                if view.mimetype == mimetype:
                    return view

        return None

    def get_func(self, path: str, mimetype: str):
        """
        Returns a decorated version (includes dynamic_params) of the view for the requested path
        """
        view = self._get_view(path, mimetype)
        dynamic_params = view.get_dynamic(path)

        def wrapper(request):
            return view(request, dynamic_params)
        return wrapper


class Error:
    def __init__(self, status):
        self.status = status
    
    
class ErrorHandler:
    def __init__(self):
        self.errors = ...
