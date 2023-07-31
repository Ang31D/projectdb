import core.script_lib as lib
import os
from tabulate import tabulate

class init:
	def __init__(self):
		self.name = '.'.join(os.path.basename(__file__).split(".")[:-1])
		self.description = "Shows help on how to use the extended script feature"
		self.requirements = []
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

	def _help_script_internals(self):
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

		help_output = self.name
		if verbose_mode:
			help_output += "\n%s" % ("-"*88)
			help_output += "\n%s" % self._help_script_internals()
			help_output += "\n%s" % ("-"*88)
		
		help_output += "\n  %s" % self.description
		# max 93 in length until new line (\n)
		# ex.:         "\n --------------------------------------------------------------------------------------------
		help_output += "\n\n"
		help_output += self._on_help()
		print(help_output)

	def _on_help(self):
		help_output  = "  Shows help on how to use the extended script feature."
		help_output += "\n  This is done through the '--script' argument, combine with '--script-args' to pass"
		help_output += "\n  options to the script."
		help_output += "\n  Use '--script-help <script>' to get help on a specific script."
		help_output += "\n"
		help_output += "\n  Use '-v' to show internal script information (useful for debugging), combine with"
		help_output += "\n  '--script-args' to see how they are rendered."
		help_output += "\n"
		help_output += "\n  Use '-v' to show internal script information (useful for debugging), combine with"
		return help_output

	def run(self, args={}):
		self._on_run()

	def _on_run(self):
		# max 93 in length until new line (\n)
		# ex.:             "\n --------------------------------------------------------------------------------------------
		#detailed_output  = "\n* being printed, it is also saved in the Nmap registry so other Nmap scripts can use it. That"
		# ^-- examples of max length, taken from: nmap --script-help smb-brute
		#detailed_output  = "\n* Extended script feature"
		help_output  = "Extended script feature\n%s" % ("-"*len("Extended script feature"))
		help_output += "\n\n  The '--script <script>' argument defines which script to run."
		help_output += "\n  Combine with '--script-args <arg-format> [<arg-format> ...]' to pass arguments to the script."
		help_output += "\n  The <arg-format> is formatted as follows: script.arg=\'<value>\'"
		help_output += "\n  Note: if only one script is passed to the '--script' argument, the <arg-format> can be specified as: arg=\'<value>\'"
		help_output += "\n"
		help_output += "\n  Use '--script-help <script>' to get help on a specific script."
		help_output += "\n"
		help_output += "\n  * Examples"
		help_output += "\n    - List available scripts"
		help_output += "\n      --script list [--script-args show='category']"
		help_output += "\n"
		help_output += "\n%s" % "  * Show Options (optional):"
		help_output += "\n%s" % "    examples          - Shows examples"
		print(help_output)