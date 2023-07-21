import core.sqlite_helper as db
import os
from tabulate import tabulate

"""
create an empty database file

--script create-db --script-args file=<file.db>
"""

class script:
	def __init__(self):
		self.name = '.'.join(os.path.basename(__file__).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Create empty database file"
		self.requirements = ["sqlite"]
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories = ["sqlite"]
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
		detailed_output  = "\n  Creates an empty sqlite database file (.db)"
		# file=<file.db>
		detailed_output += "\n  Use '--script-args' to pass arguments/options to this script."
		detailed_output += "\n"
		detailed_output += "\n  * Required options:"
		detailed_output += "\n      file='<file.db>'  - the (.db) file to create as the database"
		print(detailed_output)

	def run(self, args={}):
		if "sqlite.db_conn" not in self._extend:
			print("[!] error: %s; missing 'sqlite.db_conn' extention" % self.name)
			return

		if 'file' not in args:
			print("[!] error: %s; missing 'file' option" % self.name)
			return

		self._create_db(args)

	def _create_db(self, args):
		db_file = args['file']['value']

		if db.db_exists(db_file):
			print("[!] warning: %s; database already exists - '%s'" % (self.name, db_file))
			return

		db_conn = db.create_db(db_file)
		if db_conn is None:
			print("[!] error: %s; create database failed - '%s'" % (self.name, db_file))
			return

		db.close(db_conn)
		print("[*] database created - '%s'" % db_file)
