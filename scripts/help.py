from Script import Script
import os

class init(Script):
	def __init__(self):
		super().__init__()
		self._path = __file__
		self.name = '.'.join(os.path.basename(self._path).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Show general help on extended script"
		self._categories.append("help")

	def _on_help(self):
		# max 93 in length until new line (\n)
		# ex.:         "\n --------------------------------------------------------------------------------------------
		help_output = "  Execute the \"help\" script ('--script help') to show help on how to execute a \"script\"."
		help_output += "\n"
		help_output += "\n  To extend the code-base functionality the \"script\" feature was implemented to make it"
		help_output += "\n  easier to interact with the database for specific purposes. This is done through \"script\""
		help_output += "\n  execution. See \"EXTEND CODE-BASE\" for more info."
		help_output += "\n"
		help_output += "\n"
		title = "EXTEND CODE-BASE"
		help_output += "%s\n%s" % (title, ("-"*len(title)))
		help_output += "\n  To extend the code-base functionality the \"script\" feature was implemented to make it"
		help_output += "\n  easier to interact with the database for specific purposes. This is done through the"
		help_output += "\n  \"Script\" class inheritance (provided by 'Script.py')."
		help_output += "\n"
		help_output += "\n  The '<script>.py' file has to be located under a directory named \"Scripts\" (or a sub-"
		help_output += "\n  directory) to be recognized as a \"script\". The location of the \"Scripts\" directory"
		help_output += "\n  can be pointed out using the '--ext-script <path>' argument to separate different"
		help_output += "\n  \"script\" projects."
		help_output += "\n"
		help_output += "\n  \"BASE SCRIPT-TEMPLATE\" below shows the minimum code required. Default scripts can be"
		help_output += "\n  found at \"scripts/sqlite/\" as a reference."
		help_output += "\n"
		title = "  BASE SCRIPT-TEMPLATE"
		help_output += "\n%s" % (title)
		help_output += "\n--------------------------------------------------------------------------------------------"
		help_output += "\n"
		help_output += self._script_template_content()
		help_output += "\n--------------------------------------------------------------------------------------------"
		return help_output

	def _script_template_content(self):
		script_template = "from Script import Script"
		script_template += "\nimport os"
		script_template += "\n "
		script_template += "\nclass init(Script):"
		script_template += "\n	def __init__(self):"
		script_template += "\n		super().__init__()"
		script_template += "\n		self._path = __file__"
		script_template += "\n		self.name = '.'.join(os.path.basename(self._path).split(\".\")[:-1])"
		script_template += "\n		self.author = \"<author_name>\""
		script_template += "\n		self.description = \"<script_description>\""
		script_template += "\n		self._categories.append(\"<script_category>\")"
		script_template += "\n		self.requirements.append(\"<requirement>\") # sqlite, script-repo"
		script_template +=" \n"
		script_template += "\n	def _on_help(self):"
		script_template += "\n		# Detailed Script description and available options"
		script_template += "\n		help_output = \"  <description and options>\""
		script_template += "\n		return help_output"
		script_template +=" \n"
		script_template += "\n	def _on_run(self, args):"
		script_template += "\n		# code to run by the script"
		script_template += "\n		pass"
		return script_template

	def _on_run(self, args):
		# max 93 in length until new line (\n)
		# ex.:         "\n --------------------------------------------------------------------------------------------
		help_output = "%s - %s\n" % (self.name.upper(), self.description)
		help_output += "\n  To extend the code-base functionality the \"script\" feature was implemented to make it"
		help_output += "\n  easier to interact with the database for specific purposes. This is done through \"script\""
		help_output += "\n  execution. See \"EXTEND CODE-BASE\" during '--script-help help' for more info."
		help_output += "\n"
		help_output += "\n  The '--script <script>' argument defines which script to execute, provide a comma-"
		help_output += "\n  separated list to execute multiple scripts. Combine with '--script-args <arg-format>' to"
		help_output += "\n  pass options to the script, separate each option by a space."
		help_output += "\n"
		help_output += "\n  The <arg-format> is formatted as follows: script_name.option=\'value\'"
		help_output += "\n  NOTE: if only one script is passed through '--script' the <arg-format> can be specified"
		help_output += "\n        as: option=\'value\'."
		help_output += "\n"
		help_output += "\n  Use '--script-help <script_name>' to get help on a specific script. Add '-v' to show"
		help_output += "\n  internal script information (useful for debugging), combine with '--script-args' to view"
		help_output += "\n  parsed options."
		help_output += "\n\n"
		title = "EXAMPLES"
		help_output += "%s\n%s\n" % (title, ("-"*len(title)))
		help_output += self._on_help_examples()
		help_output += "\n"
		print(help_output)

	def _on_help_examples(self):
		# max 93 in length until new line (\n)
		# ex.:         "\n --------------------------------------------------------------------------------------------
		#title = "Examples".upper()
		#example_output  = "%s\n%s" % (title, ("-"*len(title)))
		example_output = "  * Get help on the 'list' script"
		example_output += "\n    --script-help list [-v]"
		example_output += "\n"
		example_output += "\n  * List available scripts"
		example_output += "\n    --script list [--script-args show='category,author' find=sqlite] \\"
		example_output += "\n    [--ext-script <dir-path-to-other-scripts>]"
		return example_output