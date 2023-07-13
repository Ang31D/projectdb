import core.script_lib as lib
import os

"""
list available scripts
"""

class script:
	def __init__(self):
		self.name = "list"
		self.description = "lists available scripts"
		""" self.category
			define as None to set category based on directory
		"""
		self.category = "help"
		self._set_category()

	def _set_category(self):
		if self.category is not None:
			return
		parent_dir_path = os.path.dirname(os.path.realpath(__file__))
		parent_dir_name = os.path.basename(os.path.realpath(parent_dir_path))
		if parent_dir_name == "scripts":
			self.category = "generic"
		else:
			self.category = parent_dir_name

	def help(self):
		output = "* '%s' script" % self.name
		output += "\n(category: %s)" % self.category
		output += "\n"
		output += "\n%s" % self.description
		output += "\n"
		output += "\nargs:"
		output += "\n  help \n\t- Show this help message and exit"
		output += "\n  category <type> \n\t- Filter list based on category, comma separated list."
		output += "\n  \t  Set <type> as 'category' to show a list of categories"
		
		print(output)

	def run(self, args={}):
		#lib_root_dir = lib.root_dir()
		
		if "help" in args:
			self.help()
			return

		self.list_scripts(args)
		
	def list_scripts(self, args):
		lib_root_dir = lib.root_dir()
		if not os.path.isdir(lib_root_dir):
			print("[!] error: folder not found - '%s'" % (lib_root_dir))
			return

		script_repo = lib.repo()

		print("Available scripts\n%s" % ("-"*len("Available scripts")))
		if len(list(script_repo["list"].keys())) > 0:
			print("")
		
		for script_type in list(script_repo["list"].keys()):
			print("* %s" % script_type)
			script_type_repo = script_repo["list"][script_type]
			for script in script_type_repo:
				script_info = script["name"]
				
				# convert absolute to relative path
				lib_parent_dir = os.path.dirname(lib_root_dir)
				script_rel_path = os.path.join(lib_root_dir[len(lib_parent_dir):], script["filename"])
				script_info = "%s - .%s" % (script_info, script_rel_path)
				script_rel_path = lib_root_dir[len(lib_parent_dir):]

				print("  %s" % script_info)