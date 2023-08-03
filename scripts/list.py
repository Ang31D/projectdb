from Script import Script
import core.script_lib as lib
import os
from tabulate import tabulate

"""
list available scripts

--ext-script projects/csrid/scripts --script list --script-args  list-by='category' show='script-description'
"""

class init(Script):
	def __init__(self):
		super().__init__()
		self._path = __file__
		self.name = '.'.join(os.path.basename(self._path).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Lists available scripts"
		self.requirements.append("script-repo")
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories.append("help")

	
	def _on_help(self):
		help_output  = "  Lists available scripts that can be executed through the '--script' argument."
		help_output += "\n  Use '--script list-class --script-help <script>' to view help of each script."
		help_output += "\n"
		help_output += "\n  * Options:"
		help_output += "\n    find='<value>'  - (optional) search for <value>, match on script name or description"
		help_output += "\n"
		help_output += "\n  To show further details, use the 'show' script option:"
		help_output += "\n    --script-args show='<option>[,<option>]'"
		help_output += "\n    * Options:"
		help_output += "\n      category    - shows the categories for the script"
		help_output += "\n      author      - shows the author of the script"
		help_output += "\n      script-path - shows the script location"
		help_output += "\n"
		help_output += "\n  To filter based on category, use --script-args category=<category>[,<category>]"
		help_output += "\n"
		help_output += "\n  To list by categories, use --script-args list-by=category."
		help_output += "\n      To show the script in the category, use --script-args show='category-script'"
		return help_output

	def _on_run(self, args):
		if "list-by" in args and args["list-by"]["value"] == "category":
			self._list_by_categories(args)
		else:
			self._list_scripts(args)
		
	def _list_scripts(self, args):
		repo_dir = self._extend["script.repo-dir"]
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
		search_for = None
		if "find" in args:
			search_for = args["find"]["value"]
		
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

			script_item = ["  ", script["name"], ":"]
			script_desc = script["description"]
			if len(script_desc) == 0:
				script_desc = "<missing>"
			script_item.append(script_desc)
			module = lib.get_script_module(script["module_path"])
			if module is None:
				table.append(script_item)
				continue
			script_module = module.init()
			if len(show_options) > 0:
				module = lib.get_script_module(script["module_path"])
				if "category" in show_options:
					script_item.append(":")
					script_item.append("%s" % ', '.join(script_module.categories))
				if "author" in show_options:
					script_item.append("#")
					script_item.append("[%s]" % script["author"])
				if "script-path" in show_options:
					if "author" not in show_options:
						script_item.append("#")
					if script["path"].startswith(os.path.dirname(lib.root_dir())):
						script_item.append(".%s" % script["path"][len(os.path.dirname(lib.root_dir())):])
					else:
						script_item.append("%s" % script["path"])
			if len(category_filter) > 0:
				found_category = False
				for category in script_module.categories:
					if category in category_filter:
						found_category = True
				if not found_category:
					continue

			if search_for is not None:
				found_match = False
				if search_for.lower() in script["name"].lower():
					found_match = True
				if search_for.lower() in script_desc.lower():
					found_match = True
				if search_for.lower() in script["author"].lower():
					found_match = True
				for category in script_module.categories:
					if search_for.lower() in category.lower():
						found_match = True
				if not found_match:
					continue

			table.append(script_item)
		print(tabulate(table, tablefmt='plain'))

	def _list_by_categories(self, args):
		print("NOT YET FULLY DONE")
		print("list_categories")
		repo_dir = self._extend["script.repo-dir"]
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
			script_module = module.init()
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