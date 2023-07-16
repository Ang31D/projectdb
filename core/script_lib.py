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

def _get_script_categories(script_path):
	if not os.path.isfile(script_path):
		return ''

	self_cat = ''
	with open(script_path, 'r') as f:
		content = f.read()
		if "class script:" not in content:
			return ''
		if "self._categories" in content and "def __init__(self" in content:
			init_pos_index = content.index("def __init__(self")
			content = content[init_pos_index:]
			pattern = r'self._categories ?= ?\[ ?"([^"]+)'
			script_arg_list = re.findall(pattern, content)
			if len(script_arg_list) == 1:
				self_cat = script_arg_list[0]
	return self_cat
def _get_script_description(script_path):
	self_desc = ''
	if not os.path.isfile(script_path):
		return self_desc
	with open(script_path, 'r') as f:
		content = f.read()
		if "self.description" in content and "def __init__(self" in content and "class script:" in content:
			init_pos_index = content.index("def __init__(self")
			content = content[init_pos_index:]
			pattern = r'self.description ?= ?"([^"]+)'
			script_arg_list = re.findall(pattern, content)
			if len(script_arg_list) == 1:
				self_desc = script_arg_list[0]
	return self_desc
def _get_repo_from_dir(repo_dir):
	repo_list = {}

	lib_root_dir = root_dir()
	repo_dir_path = os.path.realpath(repo_dir)
	if not repo_dir.startswith("/"):
		work_dir = os.getcwd()
		repo_dir_path = os.path.join(work_dir, repo_dir)

	if not os.path.isdir(repo_dir_path):
		return repo_list
	parent_repo_dir = os.path.dirname(repo_dir_path)
	for root, subdirs, files in os.walk(repo_dir_path):
		item_name = os.path.basename(root)
		if item_name.startswith("_"):
			continue
		if item_name in exclude_items:
			continue

		script_type = ""
		if repo_dir_path == root:
			script_type = "generic"
		else:
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
			module_path = file_path[len(parent_repo_dir)+1:]
			module_folder = os.path.dirname(module_path)
			module_path = module_path.replace("/", ".")
			module_path = '.'.join(module_path.split(".")[:-1])

			if repo_dir_path != lib_root_dir:
				# // set module_path
#				print("file_path: %s" % file_path)
				script_index = file_path.index(repo_dir)
				module_path = file_path[script_index:]
				module_path = '.'.join(module_path.split(".")[:-1]).replace("/", ".")
				if module_path.startswith("."):
					print("[!] SOMETHING WENT WRONG")

			script_item = {}
			script_item["type"] = script_type
			script_item["name"] = file_basename
			script_item["description"] = _get_script_description(file_path)
			script_item["categories"] = _get_script_categories(file_path)
			script_item["filename"] = file_name
			script_item["path"] = file_path
			script_item["module_path"] = module_path

			script_ref = file_path[len(repo_dir_path)+1:]
			script_ref = os.path.dirname(script_ref)
			if len(script_ref) > 0:
				script_ref = '.'.join(script_ref.split("/"))
				script_ref = "%s.%s" % (script_ref, file_basename)
			else:
				script_ref = file_basename

			script_item["script-ref"] = script_ref
			if script_item["path"] not in repo_list:
				repo_list[script_item["path"]] = script_item

	return repo_list
def _extend_repo_list(repo_list, repo_dir):
	if repo_dir is None:
		return repo_list
	ext_repo_list = repo_list

	other_repo_list = _get_repo_from_dir(repo_dir)
	for script_path in other_repo_list:
		script = other_repo_list[script_path]
		if script_path in ext_repo_list:
			ext_repo_list[script_path] = script
		else:
			ext_repo_list[script["path"]] = script
	return ext_repo_list
			
def repos(repo_dir=None):
	repo_list = {}

	lib_root_dir = root_dir()

	repo_list = _get_repo_from_dir(lib_root_dir)
	if repo_dir is not None:
		repo_list = _extend_repo_list(repo_list, repo_dir)
	return repo_list

def get_script_from_repo(script_name, script_repo):
	for script_path in script_repo:
		script = script_repo[script_path]
		if script["name"] == script_name:
			return script
	return None
def get_script_from_repo_dir(script_name, repo_dir):
	script_repo = repos(repo_dir)
	for script_path in script_repo:
		script = script_repo[script_path]
		if script["name"] == script_name:
			return script
	return None

def parse_script_help(scripts_string):
	scripts = {}

	if scripts_string is None:
		return scripts

	script_list = scripts_string.split(",")
	for script in script_list:
		script_name = script.strip()
		scripts[script_name] = {"name": script_name}
	return scripts


def parse_script_arg_string(script_arg_string):
	# ex. list.more='less'
	# ex. list.set_var='more=less'
	script_arg_names = script_arg_string.split("=")[0]
	arg_value = '='.join(script_arg_string.split("=")[1:])
	script_name = ''
	if "." in script_arg_names:
		script_name = script_arg_names.split(".")[0]
		arg_name = script_arg_names.split(".")[1]
	else:
		arg_name = script_arg_names
	#script_name = script_arg_names.split(".")[0]
	#arg_name = script_arg_names.split(".")[1]
	script_arg = {"name": arg_name, "value": arg_value, "script": script_name, "raw": script_arg_string}
	return script_arg
def parse_raw_script_args(scripts_string, raw_script_args):
	"""
		--script-args <script_name>.<arg_name>='<arg_value>' <script_name>.<arg_name>='<arg_value>'
	"""
	script_args = {}

	script_list = scripts_string.split(",")
	for script in script_list:
		script_name = script.strip()
		if script_name not in script_args:
			script = {"name": script_name, "args": {}, "path": None}
			script_args[script_name] = script

		if raw_script_args is None:
			continue

	if raw_script_args is None:
		return script_args
	for script_arg_string in raw_script_args:
		script_arg = parse_script_arg_string(script_arg_string)
		""" support script_arg_string without prefixed "<script_name>." for single script
			if there is only one script defined; --script <script>,
			we only need to specify the arg_name
		"""
		if len(script_arg["script"]) == 0 and len(list(script_args)) == 1:
			script_arg["script"] = list(script_args)[0]
		script_name = script_arg["script"]

		if script_name in script_args:
			arg_name = script_arg["name"]
			script_args[script_name]["args"][arg_name] = script_arg

	return script_args
def parse_script_args(scripts_string, args_string):
	"""
		--script-args <script_name>.<arg_name>='<arg_value>',<script_name>.<arg_name>='<arg_value>'
	"""
	script_args = {}
	print("args_string: '%s'" % args_string)

	script_list = scripts_string.split(",")
	for script in script_list:
		script_name = script.strip()
		if script_name not in script_args:
			script = {"name": script_name, "args": {}, "path": None}
			script_args[script_name] = script

		if args_string is None:
			continue

		pattern = r',?(%s\.[a-z-]+)=' % script_name
		script_arg_list = re.findall(pattern, args_string)
		print("[*] script_arg_list (re.findall): '%s'" % script_arg_list)
		print("[*] script_arg_list (re.findall).count: '%s'" % len(script_arg_list))
		script_arg_list_count = len(script_arg_list)
	
		for i in range(script_arg_list_count):
			script_arg_names = script_arg_list[i]
			script_arg_starts_at = args_string.index(script_arg_names)
			script_arg_string = args_string[script_arg_starts_at:]
			current_script_arg_list = re.findall(pattern, script_arg_string)
			if len(current_script_arg_list) > 1:
				next_script_arg = current_script_arg_list[1]
				next_script_arg_stars_at = script_arg_string.index(",%s=" % next_script_arg)
				script_arg_string = script_arg_string[:next_script_arg_stars_at]
			elif len(current_script_arg_list) == 0:
				continue

			script_arg = parse_script_arg_string(script_arg_string)
			script_name = script_arg["script"]
			if script_name in script_args:
				arg_name = script_arg["name"]
				script_args[script_name]["args"][arg_name] = script_arg

	return script_args

def get_script_module(module_path):
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