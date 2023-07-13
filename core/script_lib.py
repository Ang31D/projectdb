import config
import os
import pathlib
from collections import OrderedDict
import re
import sys
import importlib

exclude_items = ["__pycache__", "__init__"]

def root_dir():
	core_dir = os.path.dirname(os.path.realpath(__file__))
	root_dir = os.path.dirname(core_dir)
	#return os.path.join(root_dir, config.SCRIPTS_DIR_NAME)
	return os.path.join(root_dir, "scripts")

def repo():
	repo_list = {"list": {}}
	lib_root_dir = root_dir()
	for root, subdirs, files in os.walk(lib_root_dir):
		#print("root - %s" % root)
		item_name = os.path.basename(root)
		if item_name.startswith("_"):
			continue
		if item_name in exclude_items:
			#print("[-] SKIPPING - item_name.item_name: %s" % item_name)
			continue

		script_type = ""
		if lib_root_dir == root:
			#print("**** Generic (scripts)")
			script_type = "generic"
		else:
			#print("**** %s (scripts)" % item_name)
			script_type = item_name

		for file_name in files:
			file_ext = pathlib.Path(file_name).suffix
			if file_ext != config.SCRIPT_EXT:
				continue

			file_basename = pathlib.Path(file_name).stem
			if file_basename.startswith("_"):
				continue
			if file_basename in exclude_items:
				continue
			file_path = os.path.join(root, file_name)

			script_item = {}
			script_item["type"] = script_type
			script_item["name"] = file_basename
			script_item["filename"] = file_name
			script_item["path"] = file_path
			if script_type not in repo_list["list"]:
				repo_list["list"][script_type] = []
			repo_list["list"][script_type].append(script_item)
	return repo_list
def repos():
	repo_list = {}
	lib_root_dir = root_dir()
	#print("lib_root_dir: '%s'" % lib_root_dir)
	parent_lib_dir = os.path.dirname(lib_root_dir)
	#print("parent_lib_dir: '%s'" % parent_lib_dir)
	for root, subdirs, files in os.walk(lib_root_dir):
		item_name = os.path.basename(root)
		if item_name in exclude_items:
			#print("[-] SKIPPING - item_name.item_name: %s" % item_name)
			continue

		script_type = ""
		if lib_root_dir == root:
			#print("**** Generic (scripts)")
			script_type = "generic"
		else:
			#print("**** %s (scripts)" % item_name)
			script_type = item_name

		for file_name in files:
			file_ext = pathlib.Path(file_name).suffix
			if file_ext != config.SCRIPT_EXT:
				continue

			file_basename = pathlib.Path(file_name).stem
			if file_basename in exclude_items:
				continue
			file_path = os.path.join(root, file_name)
			module_path = file_path[len(parent_lib_dir)+1:].replace("/", ".")
			module_path = '.'.join(module_path.split(".")[:-1])
			#print(module_path)

			script_item = {}
			script_item["type"] = script_type
			script_item["name"] = file_basename
			script_item["filename"] = file_name
			script_item["path"] = file_path
			script_item["module_path"] = module_path
			if script_item["path"] not in repo_list:
				repo_list[script_item["path"]] = script_item
	return repo_list

def parse_script_help(scripts_string):
	if scripts_string is None:
		print("[*] parse_script_args() - no script passed")
		return

	scripts = {}

	script_list = scripts_string.split(",")
	for script in script_list:
		script_name = script.strip()
		scripts[script_name] = {"name": script_name}
	return scripts

		
def parse_script_args(scripts_string, args_string):
	#--script-arg <script>.<arg>='<arg_value>'
	#script_arg
	""" no script arguments passed
	"""
	print("scripts_string: '%s'" % scripts_string)
	print("args_string: '%s'\n" % args_string)

	if args_string is None:
		print("[*] parse_script_args() - no script arguments passed")
		#return

	scripts = {}
	script_args = {}

	show_help_for_scripts = []

	script_list = scripts_string.split(",")
	for script in script_list:
		script_name = script.strip()
		if script_name not in script_args:
			script = {"name": script_name, "args": {}, "path": None}
			script_args[script_name] = script

		if args_string is None:
			continue

		# // check for script help
		pattern = r',?(%s\.help)$|,(%s\.help),' % (script_name, script_name)
		#pattern = r',?(%s\.help)[$,]+' % (script_name)
		script_help_list = re.findall(pattern, args_string)
		print("script_help_list: '%s'" % script_help_list)
		if len(script_help_list) > 0:
			for help_matches in list(script_help_list):
				print("**** help_matches")
				print(help_matches)
				for help_match in help_matches:
					print("**** help_match: '%s'" % help_match)
					if len(help_match) > 0:
						print("help_match: YES")
						show_help_for_scripts.append(help_match)
						script["args"]["help"] = {"name": script_name, "arg_name": "help", "arg_value": "show", "raw": help_match}

		script_args[script_name] = script
		print("show_help_for_scripts: '%s'" % show_help_for_scripts)
	
#	for script_name in script_args:
#		print(script_args[script_name])

	#script_arg = args_string
	if args_string is None:
		args_string = ''
	arg_script_name = args_string.split(".")[0]
	if script_name == arg_script_name:
		pass
		#print("arg-script_name '%s' matches script_name '%s'" % (arg_script_name, script_name))

	pattern = r',?([a-z.-]+)='
	#pattern = r",?%s([a-z.-]+)=" % script_name
	print("[*] args_string: '%s'" % args_string)
	script_arg_list = re.findall(pattern, args_string)
	print("[*] script_arg_list (re.findall): '%s'" % script_arg_list)
	
	if len(script_arg_list) == 1:
		print(args_string)
		return

	for i in range(len(script_arg_list)):
		script_arg = script_arg_list[i]
		script_arg_starts_at = args_string.index(script_arg)
		#print("[%s] starts_at: %s" % (script_arg, script_arg_starts_at))

		if i >= len(script_arg_list)-1:
			script_arg_string = args_string[script_arg_starts_at:]
		else:
			next_script_arg = script_arg_list[i+1]
			next_script_arg_starts_at = args_string.index(next_script_arg)
			script_arg_string = args_string[script_arg_starts_at:next_script_arg_starts_at-script_arg_starts_at]
			print("script_arg_string: '%s'" % script_arg_string)
			if len(script_arg_string) > 0 and script_arg_string[-1] == ",":
				script_arg_string = script_arg_string[:-1]

		#print("\t%s" % script_arg_string)
		script_name = script_arg_string.split(".")[0]
		#script_arg = script_arg_string.split(".")[1].split("=")[0]
		arg_name = script_arg_string.split(".")[1].split("=")[0]
		arg_value = script_arg_string.split("=")[1]
		script = {"name": script_name, "arg_name": arg_name, "arg_value": arg_value, "raw": script_arg_string}
		#script_arg = {"name": arg_name, "value": arg_value, "raw": script_arg_string}
		script_arg = {"name": arg_name, "value": arg_value}
		if script_name in script_args:
			script_args[script_name]["args"][arg_name] = script_arg

		#print("\t%s" % script)

	for script_name in script_args:
		script = script_args[script_name]
		print("\tscript: '%s'" % script["name"])
		for arg_name in script["args"]:
			script_arg = script["args"][arg_name]
			#print(script_arg)
			print("\t  arg: '%s'" % script_arg)

	return script_args


#def run(script, script_args):
#	print(script)
#def get_script_module_by_path(module_path):
def get_script_module(module_path):
	script = None
	script = importlib.import_module(module_path)
	return script
def script_path_as_module_path(script_path):
	lib_root_dir = root_dir()
	parent_lib_dir = os.path.dirname(lib_root_dir)
	
	module_path = script_path[len(parent_lib_dir)+1:]
	module_path = '.'.join(module_path.split("/"))
	if module_path.endswith(".py"):
		module_path = module_path[:len(module_path)-len(".py")]
	else:
		module_path = None
	return module_path
def get_script_path_by_name(script_name):
	script_path = '/'.join(script_name.split("."))
	script_path = "scripts/%s.py" % script_path
	return os.path.realpath(script_path)
	return script_path
def get_scripts():
	scripts = []
	feed_list = get_feed_list()
	for feed_name in feed_list:
		feeds.append(core.feed.get_feed(feed_name))
	return feeds