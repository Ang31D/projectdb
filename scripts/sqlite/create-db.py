from Script import Script
import core.sqlite_helper as db
import os
from tabulate import tabulate

"""
create an empty database file

--script create-db --script-args file=<file.db>
"""

class init(Script):
	def __init__(self):
		super().__init__()
		self._path = __file__
		self.name = '.'.join(os.path.basename(self._path).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Create empty database file"
		self.requirements.append("sqlite")
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories.append("sqlite")

	def _on_help(self):
		help_output  = "  Creates an empty sqlite database file (.db)"
		# file=<file.db>
		help_output += "\n  Use '--script-args' to pass arguments/options to this script."
		help_output += "\n"
		help_output += "\n  * Required options:"
		help_output += "\n      file='<file.db>'  - the (.db) file to create as the database"
		return help_output

#	def run(self, args={}):
#		if "sqlite.db_conn" not in self._extend:
#			print("[!] error: %s; missing 'sqlite.db_conn' extention" % self.name)
#			return
#
#		if 'file' not in args:
#			print("[!] error: %s; missing 'file' option" % self.name)
#			return
#
#		self._create_db(args)
	def _on_run(self, args):
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
