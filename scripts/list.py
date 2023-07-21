import core.script_lib as lib
import os
from tabulate import tabulate

"""
list available scripts

--ext-script projects/csrid/scripts --script list --script-args  list-by='category' show='script-description'
"""

class script:
	def __init__(self):
		self.name = '.'.join(os.path.basename(__file__).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Lists available scripts"
		self.requirements = ["script-repo"]
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories = ["help"]
		self._extend = {}
		self._set_categories()
		self._script_repo_dir = None

	@property
	def categories(self):
		return self._categories

	def extend(self, data={}):
		key_list = list(data.keys())
		if len(key_list) == 0:
			return
		for key in key_list:
			self._extend[key] = data[key]

	def _set_categories(self):
		parent_dir_path = os.path.dirname(os.path.realpath(__file__))
		parent_dir_name = os.path.basename(os.path.realpath(parent_dir_path))
		if parent_dir_name == "scripts":
			self._categories.append("generic")
		else:
			if "/scripts/" in parent_dir_path:
				dir_index = parent_dir_path.rindex("/scripts/")
				scripts_root_dir = parent_dir_path[dir_index+1:]
				dir_names = scripts_root_dir.split("/")[1:]
				for dir_name in dir_names:
					if dir_name not in self._categories:
						self._categories.append(dir_name)
			elif parent_dir_name not in self._categories:
				self._categories.append(parent_dir_name)

	def _script_internals(self):
		data = ""
		if "_internal.script" in self._extend:
			data = "[INTERNALS]"
			int_table = []
			for key in self._extend["_internal.script"]:
				int_table.append(["  ", "%s" % key, ":", "%s" % self._extend["_internal.script"][key]])
			
			data += "\n%s" % tabulate(int_table, tablefmt='plain')
			if "_internal.script.args" in self._extend:
				script_args = self._extend["_internal.script.args"]
				if self.name in script_args and "args" in script_args[self.name]:
					args = script_args[self.name]["args"]
					data += "\n\n  * Options"
					if len(list(args)) > 0:
						int_table = []
						for key in args:
							int_table.append(["  ", "%s" % key, ":", "%s" % args[key]["value"]])
						data += "\n%s" % tabulate(int_table, tablefmt='plain')
				else:
					data += "\n%s" % script_args
		else:
			data += "\n%s" % "[!] error: extention not found - '%s'" % "_internal.script"
		return data
	def help(self):
		verbose_mode = False
		if "_internal.verbose_mode" in self._extend:
			verbose_mode = self._extend["_internal.verbose_mode"]

		output = self.name
		output += "\nCategories: %s" % ' '.join(self.categories)
		output += "\nRequirements: %s" % ' '.join(self.requirements)
		print(output)
		if verbose_mode:
			print("-"*88)
			print(self._script_internals())
			print("-"*88)
		else:
			print("%s" % __file__)
			pass
		output = "  %s" % self.description
		print(output)
		# max 93 in length until new line (\n)
		# ex.:             "\n --------------------------------------------------------------------------------------------
		detailed_output  = "\n  Lists available scripts that can be executed through the '--script' argument."
		detailed_output += "\n  Use '--script-help <script>' to view help of each script."
		detailed_output += "\n"
		detailed_output += "\n\n  To show further details, use the 'show' script option:"
		detailed_output += "\n    --script-args show='<option>[,<option>]'"
		detailed_output += "\n    * Options:"
		detailed_output += "\n      category    - shows the categories for the script"
		detailed_output += "\n      script-path - shows the script path"
		detailed_output += "\n\n  To filter based on category, use --script-args category=<category>[,<category>]"
		detailed_output += "\n\n  To list by categories, use --script-args list-by=category."
		detailed_output += "\n      To show the script in the category, use --script-args show='category-script'"
		print(detailed_output)

	def run(self, args={}):
		if "script.repo-dir" in self._extend:
			self._script_repo_dir = self._extend["script.repo-dir"]
		else:
			print("[!] error: extention not found - '%s'" % "script.repo-dir")
			return

		if "list-by" in args and args["list-by"]["value"] == "category":
			self._list_by_categories(args)
		else:
			self._list_scripts(args)
		
	def _list_scripts(self, args):
		repo_dir = self._script_repo_dir
		if not os.path.isdir(repo_dir):
			print("[!] error: repo-dir not found - '%s'" % (repo_dir))
			return

		verbose_mode = False
		if "_internal.verbose_mode" in self._extend:
			verbose_mode = self._extend["_internal.verbose_mode"]

		script_repo = lib.repos(repo_dir)

		print("Available scripts\n%s" % ("-"*len("Available scripts")))
		if len(list(script_repo.keys())) > 0:
			print("")
		
		current_script_type = None
		table = []
		
		show_options = []
		if "show" in args:
			for option in args["show"]["value"].split(","):
				show_options.append(option.strip())
		category_filter = []
		if "category" in args:
			for category in args["category"]["value"].split(","):
				category_filter.append(category.strip())
		for script_path in list(script_repo.keys()):
			script = script_repo[script_path]
			# convert absolute to relative path
			#lib_parent_dir = os.path.dirname(repo_dir)
			#script_rel_path = os.path.join(repo_dir[len(lib_parent_dir):], script["filename"])
			#rel_module_path = '.'.join(script["module_path"].split(".")[1:])

			script_item = ["  ", script["name"], ":"]
			script_desc = script["description"]
			if len(script_desc) == 0:
				script_desc = "<missing>"
			script_item.append(script_desc)
			module = lib.get_script_module(script["module_path"])
			if module is None:
				table.append(script_item)
				continue
			script_module = module.script()
			if len(show_options) > 0:
				module = lib.get_script_module(script["module_path"])
				if "category" in show_options:
					#script_item.append("(%s)" % ', '.join(script_module.categories))
					script_item.append("#")
					script_item.append("%s" % ', '.join(script_module.categories))
				if "script-path" in show_options:
					#script_item.append("#")
					#script_item.append("%s" % script["path"])
					script_item.append("(%s)" % script["path"])
			if len(category_filter) > 0:
				found_category = False
				for category in script_module.categories:
					if category in category_filter:
						found_category = True
				if not found_category:
					continue

			table.append(script_item)
		print(tabulate(table, tablefmt='plain'))

	def _list_by_categories(self, args):
		print("NOT YET FULLY DONE")
		print("list_categories")
		repo_dir = self._script_repo_dir
		if not os.path.isdir(repo_dir):
			print("[!] error: repo-dir not found - '%s'" % (repo_dir))
			return

		verbose_mode = False
		if "_internal.verbose_mode" in self._extend:
			verbose_mode = self._extend["_internal.verbose_mode"]

		script_repo = lib.repos(repo_dir)

		table = []
		categories = {}
		print("Script categories\n%s" % ("-"*len("Script categories")))
		#if len(list(script_repo.keys())) > 0:
		#	print("")

		category_filter = []
		if "category" in args:
			for category in args["category"]["value"].split(","):
				category_filter.append(category.strip())
		
		show_options = {}
		if "show" in args:
			for option in args["show"]["value"].split(","):
				option_name = option.strip()
				show_options[option_name] = True


		for script_path in list(script_repo.keys()):
			script = script_repo[script_path]
			module = lib.get_script_module(script["module_path"])
			if module is None:
				continue
			script_module = module.script()
			#print(script_module.categories)
			for category in script_module.categories:
				if len(category_filter) > 0:
					if category not in category_filter:
						continue
				if category not in categories:
					categories[category] = []
				categories[category].append(script_path)
		#print('\n'.join(list(categories)))

		for category in categories:
			table = []
			output = ''
			if len(show_options) > 0:
				#output = '\n'
				pass
			output = "* %s" % category
			#print("\n* %s" % category)
			print(output)
			script_item=[]
			#script_item.append("* %s" % category)
			#table.append(script_item)
			if len(show_options) == 0:
				#continue
				pass

			for script_path in categories[category]:
				script_item=[""]
				#print(script_path)
				script = script_repo[script_path]
				#script_item = script["name"]
				script_item.append("%s" % script["name"])
				#if "script-description" in show_options:
				if 1==1 or "script-description" in show_options:
					script_item.append(":")
					script_desc = script["description"]
					if len(script_desc) == 0:
						script_desc = "<missing>"
					script_item.append(script_desc)
					#script_item.append("%s" % script["description"])
				if "script-path" in show_options:
					script_item.append("#")
					script_item.append(script["path"])
				else:
					pass
					#print(script["name"])
				#script_item += " "
				#print(script_item)
				#script_item = ["  ", script["name"], ":"]
				table.append(script_item)
			print(tabulate(table, tablefmt='plain'))