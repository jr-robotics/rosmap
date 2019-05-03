import pkgutil
import importlib
import inspect
import logging

class ModuleLoader(object):
    """
    Loads modules via reflection and automatically instantiates classes.
    """
    @staticmethod
    def load_modules(dir_path: str, package: str, ignore_classes: list, class_suffix: str, *args) -> list:
        """
        Creates a list of objects from all classes found in a package.
        :param dir_path: current path (i.e.: path of the calling file).
        :param package: path to package starting from dir_path,
        :param ignore_classes: Ignores classes named in this list. (list contains strings)
        :param class_suffix: Selects only classes that end with this suffix.
        :param args: Arguments for the class' constructor.
        """

        # create list.
        objects = list()

        logging.info('[ModuleLoader]: Initializing parsers at ' + dir_path + '/' + package)

        # get modules iterator.
        modules = pkgutil.iter_modules(path=[dir_path + '/' + package])

        # notify if there are no modules inside the folder.
        if not modules:
            logging.warning('[ModuleLoader]: No modules found at' + dir_path)
            return objects

        # iterate over modules.
        for loader, mod_name, ispkg in modules:

            # Get actual module path...
            module_path = package.replace("/", ".")

            # Import module.
            mod = importlib.import_module("rosmap." + module_path + "." + mod_name)

            # Get class names from module and instantiate classes.
            for selected_classname in ModuleLoader.get_classnames_from_module(mod, class_suffix, ignore_classes):
                try:
                    objects.append(ModuleLoader.instantiate_class(mod, mod_name, module_path, selected_classname, *args))
                except ValueError as error:
                    logging.warning("[ModuleLoader]: " + str(error))

        return objects



    @staticmethod
    def get_classnames_from_module(module: str, class_suffix: str, ignore_classes: list) -> iter:
        """
        Yield returns all applicable class-names in a module...
        :param module: The module to search classes in.
        :param class_suffix: Selects only classes that end with this suffix.
        :param ignore_classes: Ignores classes named in this list. (list contains strings)
        :return: iterable of strings containing selected class-names.
        """
        # Iterate over all classes in module.
        for classname in dir(module):
            if classname[-len(class_suffix):] == class_suffix and classname not in ignore_classes:
                yield classname

    @staticmethod
    def instantiate_class(module: str, module_name: str, module_path: str, class_name: str, *args) -> object:
        """
        Instantiates a class based on parameters.
        :param module: The module the class is located in.
        :param module_name: The name of the module the class is located in.
        :param module_path: The path to the module.
        :param class_name: The name of the class to be instantiated.
        :param args: Arguments for the class' constructor.
        :return: instance of the selected class in the selected module.
        """
        my_class = getattr(module, class_name)
        logging.info("[ModuleLoader]: Instantiating " + class_name + " from " + module_path + "." + module_name)
        if inspect.isclass(my_class):
            return my_class(*args)
        else:
            raise ValueError(class_name + " is not a class, skipping.")
