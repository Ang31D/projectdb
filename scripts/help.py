import core.script_lib as lib
import os
from tabulate import tabulate

"""
list available scripts
"""

class script:
	def __init__(self):
		self.name = '.'.join(os.path.basename(__file__).split(".")[:-1])
		self.description = "Help on how to use the extended script feature"
		self.requirements = [""]
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
		detailed_output  = "\n  Shows help on how to use the extended script feature."
		detailed_output += "\n  This is done through the '--script' argument."
		detailed_output += "\n  Combine with '--script-args' to pass arguments to the script."
		detailed_output += "\n  Use '--script-help <script>' to get help on a specific script."
		print(detailed_output)

	def run(self, args={}):
		self.show_help()

	def show_help(self):
		#detailed_output  = "\n* being printed, it is also saved in the Nmap registry so other Nmap scripts can use it. That"
		# ^-- examples of max length, taken from: nmap --script-help smb-brute
		detailed_output  = "\n* Extended script feature"
		detailed_output += "\n\n  The '--script <script>' argument defines which script to run."
		detailed_output += "\n  Combine with '--script-args <arg-format> [<arg-format> ...]' to pass arguments to the script."
		detailed_output += "\n  The <arg-format> is formatted as follows: script.arg=\'<value>\'"
		detailed_output += "\n  Note: if only one script is passed to the '--script' argument, the <arg-format> can be specified as: arg=\'<value>\'"
		detailed_output += "\n"
		detailed_output += "\n  Use '--script-help <script>' to get help on a specific script."
		detailed_output += "\n"
		detailed_output += "\n  * Examples"
		detailed_output += "\n    - List available scripts"
		detailed_output += "\n      --script list [-v]"
		print(detailed_output)