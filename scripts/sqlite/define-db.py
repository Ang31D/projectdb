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
		self.description = "Define database table"
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
		detailed_output  = "\n  Defines the sqlite database; create table through their definition file"
		detailed_output += "\n  Use '--script-args' to pass options to this script."
		detailed_output += "\n\n  * Options:"
		detailed_output += "\n    db='<file.db>'        - the database (.db) file to define"
		detailed_output += "\n    file='<table.sql>'    - the \"definition file\" that describes the table"
		detailed_output += "\n\n    table='<table_name>'  - (optional) overrides table name to define; otherwise"
		detailed_output += "\n                            the table name is defined by the definition file"
		detailed_output += "\n\nSample \"definition file\" (<table.sql>):"
		detailed_output += "\n%s" % ("-"*88)
		detailed_output += """\nCREATE TABLE hash_map(
        md5 text,
        sha_256 text,
        comment text
        )"""
		detailed_output += "\n%s" % ("-"*88)

		print(detailed_output)

	def run(self, args={}):
		if "sqlite.db_conn" not in self._extend:
			print("[!] error: %s; missing 'sqlite.db_conn' extention" % self.name)
			return

		# // check requirements
		if 'db' not in args:
			print("[!] error: %s; missing 'db' option" % self.name)
			return
		if 'file' not in args:
			print("[!] error: %s; missing 'file' option" % self.name)
			return

		self._define_db(args)

	def _connect_db(self, db_file):
		if not db.db_exists(db_file):
			print("[!] error: %s; database failed to connect - missing file '%s'" % (self.name, db_file))
			return None
		db_conn = db.connect(db_file)
		if db_conn is None:
			print("[!] error: %s; database failed to connect - '%s'" % (self.name, db_file))
			return None
		return db_conn

	def _define_db(self, args):
		verbose_mode = False
		if "_internal.verbose_mode" in self._extend:
			verbose_mode = self._extend["_internal.verbose_mode"]

		db_file = args['db']['value']
		definition_file = args['file']['value']
		table_name = None
		if 'table' in args:
			table_name = args['table']['value']

		db_conn = self._connect_db(db_file)
		if db_conn is None:
			return
	
		table_definition = db.table_definition_from_file(definition_file)
		if table_definition is None:
			print("[!] error: %s; failed to get definition: '%s'" % (self.name, definition_file))
			db.close(db_conn)
			return
	
		defined_table_name = db.get_table_from_definition(table_definition)
		if defined_table_name is None:
			print("[!] error: %s; invalid table definition: '%s'\n%s" % (self.name, definition_file, table_definition))
			db.close(db_conn)
			return
	
		"""
			rename the table name of defined table definition
		"""
		if table_name is not None and defined_table_name != table_name:
			#print("[*] %s; renaming defined table '%s' to '%s'" % (self.name, defined_table_name, table_name))
			table_definition = db.rename_table_definition(table_definition, table_name)
			if table_definition is None:
				table_definition = db.table_definition_from_file(definition_file)
				print("[!] error: %s; rename table definition failed - new table name '%s'\n%s" % (self.name, definition_file, table_definition))
				db.close(db_conn)
				return
			table_name = table_name
		else:
			table_name = defined_table_name
	
		if db.table_exists(db_conn, table_name):
			print("[!] warning: %s; define-db; table already exists - '%s'" % (self.name, table_name))
			db.close(db_conn)
			return
	
		if not db.define_db(db_conn, table_definition):
			print("[!] error: %s; status: failed: '%s'\n%s" % (self.name, definition_file, table_definition))
			db.close(db_conn)
			return
	
		print("[*] status: success - '%s'\n%s" % (definition_file, table_definition))
		db.close(db_conn)