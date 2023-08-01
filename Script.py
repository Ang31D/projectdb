import os
from tabulate import tabulate

class Script:
	def __init__(self):
		self._path = __file__
		self.name = '.'.join(os.path.basename(self._path).split(".")[:-1])
		self.author = "**** author not defined ****"
		self.description = "  **** Script description not defined! ****"
		self.requirements = []
		self._categories = []
		self._extend = {}
		#self._args = {}
		self._on_init()

	def _on_init(self):
		self._set_categories()
		#self._init_args()

	def _init_args(self):
		self._args = {}
#		self._args["Options"] = {}
#		self._args["Options"]["find"] = {"name": "find", "type": "string", "optional": True, "metavar": "<value>", "help": "search for <value>, match on script name or description"}
#		"""
#		help_output += "\n  * Options:"
#		help_output += "\n    find='<value>'  - (optional) search for <value>, match on script name or description"
#		"""
#		
#		self._args["Options"]["show"] = {"name": "show", "type": "list", "optional": True, "metavar": "<option>", "help": "To show further details, use the 'show' script option", "items": {}}
#		self._args["Options"]["show"]["items"]["category"] = {"name": "category", "type": "item", "optional": True, "help": "shows the categories for the script"}
#		self._args["Options"]["show"]["items"]["script-path"] = {"name": "script-path", "type": "item", "optional": True, "help": "shows the script path"}
#		"""
#		help_output += "\n  To show further details, use the 'show' script option:"
#		help_output += "\n    --script-args show='<option>[,<option>]'"
#		"""
#
#		self._args["Options"]["category"] = {"name": "category", "type": "list", "optional": True, "metavar": "<category>", "help": "Filter based on category; comma separated list"}
#
#		self._args["date"]    = {"name": "date",    "type": "string", "metavar": "<date>",    "help": "Filter releases based on version."}
#		self._args["field"]   = {"name": "field",   "type": "string", "metavar": "<field>",   "help": "Filter on field (column)."}
#		self._args["value"]   = {"name": "value",   "type": "string", "metavar": "<value>",   "help": "Filter on value."}
#
#		self._args["match-condition"] = {"name": "match-condition", "type": "options", "metavar": "<cond>",   "help": "Match on condition.", "options": {}}
#		self._args["match-all"]       = {"name": "match-all",       "type": "options", "metavar": "<no|yes>", "help": "Match on all.",       "options": {}}

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
		parent_dir_path = os.path.dirname(os.path.realpath(self._path))
		parent_dir_name = os.path.basename(os.path.realpath(parent_dir_path))
		if parent_dir_name == "scripts":
			self._categories.append("generic")
		else:
			if "/scripts/" in parent_dir_path:
				dir_index = parent_dir_path.rindex("/scripts/")
				scripts_root_dir = parent_dir_path[dir_index+1:]
				#print("scripts_root_dir: %s" % scripts_root_dir)
				dir_names = scripts_root_dir.split("/")[1:]
				for dir_name in dir_names:
					if dir_name not in self._categories:
						self._categories.append(dir_name)
			#elif parent_dir_name not in self._categories:
			#	self._categories.append(parent_dir_name)

	def help(self):
		verbose_mode = False
		if "_internal.verbose_mode" in self._extend:
			verbose_mode = self._extend["_internal.verbose_mode"]

		help_output = self.name
		#help_output += "\nAuthor: %s" % self.author
		if verbose_mode:
			help_output += "\n%s" % ("-"*88)
			help_output += "\n%s" % self._script_internals()
			help_output += "\n%s" % ("-"*88)
		
		help_output += "\n  %s" % self.description
		# max 93 in length until new line (\n)
		# ex.:         "\n --------------------------------------------------------------------------------------------
		help_output += "\n\n"
		help_output += self._on_help()
		print(help_output)

	def _script_internals(self):
		data = ""
		if "_internal.script-definition" in self._extend:
			data = "[INTERNALS]"
			#data += "\n* Script Definition"
			table_data = []
			#key_order = ["name", "author", "description", "type", "categories", "requirements", "filename", "path", "module_path", "script-ref"]
			key_order = self._extend["_internal.script-definition"]
			for key in key_order:
				if key in self._extend["_internal.script-definition"]:
					key_value = self._extend["_internal.script-definition"][key]
					if type(key_value).__name__ == "list":
						key_value = ', '.join(key_value)
					#table_data.append(["  ", "%s" % key, ":", "%s" % key_value])
					table_data.append(["%s" % key, ":", "%s" % key_value])
			data += "\n%s" % tabulate(table_data, tablefmt='plain')

			if "_internal.script.args" in self._extend:
				script_args = self._extend["_internal.script.args"]
				if self.name in script_args and "args" in script_args[self.name]:
					args = script_args[self.name]["args"]
					data += "\n\n* Options (parsed)"
					if len(list(args)) > 0:
						table_data = []
						for key in args:
							table_data.append(["  ", "%s" % key, ":", "%s" % args[key]["value"]])
						data += "\n%s" % tabulate(table_data, tablefmt='plain')
				else:
					data += "\n%s" % script_args
		else:
			data += "\n%s" % "[!] error: extention not found - '%s'" % "_internal.script"
		return data

	def run(self, args={}):
		if "sqlite" in self.requirements:
			if "sqlite.db_conn" not in self._extend:
				print("[!] error: %s; missing 'sqlite.db_conn' extention" % self.name)
				return

		if "script-repo" in self.requirements:
			if "script.repo-dir" not in self._extend:
				print("[!] error: extention not found - '%s'" % "script.repo-dir")
				return
			else:
				pass
				self._script_repo_dir = self._extend["script.repo-dir"]

		self._on_run(args)

	def _on_help(self):
		# max 93 in length until new line (\n)
		# ex.:         "\n --------------------------------------------------------------------------------------------
		help_output = "\n\n  **** Help options not defined! ****"
		return help_output

	def _on_run(self, args):
		print("  **** Run (_on_run) code not defined! ****")