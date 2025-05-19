from importlib import import_module


def import_object(import_name: str):
	module_name, object_name = import_name.rsplit(".", 1)
	module = import_module(module_name)
	return getattr(module, object_name)
