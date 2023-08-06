from Script import Script
import core.sqlite_helper as db
import os

class init(Script):
	def __init__(self):
		super().__init__()
		self._path = __file__
		self.name = '.'.join(os.path.basename(self._path).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Define database table"
		self.requirements.append("sqlite")
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories.append("sqlite")

	def _on_help(self):
		help_output  = "  Defines the sqlite database; create table through their definition file"
		help_output += "\n  Use '--script-args' to pass options to this script."
		help_output += "\n"
		help_output += "\n  * Options:"
		help_output += "\n    file='<table.sql>'    - the \"definition file\" that describes the table"
		help_output += "\n"
		help_output += "\n    table='<table_name>'  - (optional) overrides table name to define; otherwise"
		help_output += "\n                            the table name is defined by the definition file"
		help_output += "\n"
		help_output += "\nSample \"definition file\" (<table.sql>):"
		help_output += "\n%s" % ("-"*88)
		help_output += """\nCREATE TABLE hash_map(
		md5 text,
		sha_256 text,
		comment text
		)"""
		help_output += "\n%s" % ("-"*88)
		return help_output

	def _on_run(self, args):
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

		definition_file = args['file']['value']
		table_name = None
		if 'table' in args:
			table_name = args['table']['value']

		#db_file = args['db']['value']
		#db_conn = self._connect_db(db_file)
		db_conn = self._extend["sqlite.db_conn"]
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