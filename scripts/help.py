from Script import Script
import os
from tabulate import tabulate

class init(Script):
	def __init__(self):
		super().__init__()
		self._path = __file__
		self.name = '.'.join(os.path.basename(self._path).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Show general help on extended script"
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories.append("help")

	def _on_help(self):
		help_output  = "  Shows help on how to use the extended script feature."
		help_output += "\n"
		help_output += "\n  Use '-v' to show internal script information (useful for debugging),"
		help_output += "\n  combine with '--script-args' to see how options are parsed."
		help_output += "\n"
		help_output += "\n  This is done through the '--script' argument, combine with '--script-args' to pass"
		help_output += "\n  options to the script."
		help_output += "\n  Use '--script-help <script>' to get help on a specific script."
		help_output += "\n"
		help_output += "\n  Use '-v' to show internal script information (useful for debugging), combine with"
		help_output += "\n  '--script-args' to see how they are rendered."
		help_output += "\n"
		help_output += "\n  Use '-v' to show internal script information (useful for debugging), combine with"
		return help_output

	def _on_run(self, args):
		# max 93 in length until new line (\n)
		# ex.:         "\n --------------------------------------------------------------------------------------------
		help_output = ""
		#help_output = "Help on extended script"
		#help_output += "\n"
		help_output += "\n  To extend the code-base functionality the \"extended script\" feature was implemented to"
		help_output += "\n  make it easier to interact with the database for specific purposes. This is done through"
		help_output += "\n  \"script\" execution. (see \"EXTEND CODE-BASE\")"
		help_output += "\n"
		#title = "Script Execution"
		#help_output += "\n%s\n%s" % (title, ("-"*len(title)))
		help_output += "\n  The '--script <script>' argument defines which script to execute, provide a comma-"
		help_output += "\n  separated list to execute multiple scripts. Combine with '--script-args <arg-format>' to"
		help_output += "\n  pass options to the script, separate each option by a space."
		help_output += "\n"
		help_output += "\n  The <arg-format> is formatted as follows: script_name.option=\'value\'"
		help_output += "\n  NOTE: if only one script is passed through '--script' the <arg-format> can be specified"
		help_output += "\n        as: option=\'value\'."
		help_output += "\n"
		help_output += "\n  Use '--script-help <script_name>' to get help on a specific script. Add '-v' to show"
		help_output += "\n  internal script information (useful for debugging), combine with '--script-args' to see"
		help_output += "\n  how options are parsed."
		help_output += "\n\n"
		title = "EXAMPLES"
		example_output  = "\n%s\n%s" % (title, ("-"*len(title)))
		help_output += self._on_help_examples()
		help_output += "\n"
		help_output += "\n%s" % "  * Show Options (optional):"
		help_output += "\n%s" % "    examples          - Shows examples"
		help_output += "\n\n"
		title = "EXTEND CODE-BASE"
		help_output += "%s\n%s" % (title, ("-"*len(title)))
		# ex.:         "\n --------------------------------------------------------------------------------------------
		help_output += "\n  To extend the functionality based on the code-base the \"extended script\" feature was"
		help_output += "\n  implemented to make it easier to interact with the database for specific goals. This is"
		help_output += "\n  done through the \"Script\" class inheritance (provided by 'Script.py')."
		print(help_output)

	def _on_help_examples(self):
		# max 93 in length until new line (\n)
		# ex.:         "\n --------------------------------------------------------------------------------------------
		title = "Examples".upper()
		example_output  = "%s\n%s" % (title, ("-"*len(title)))
		example_output += "\n  * Get help on the 'list' script"
		example_output += "\n    --script-help list [-v]"
		example_output += "\n"
		example_output += "\n  * List available scripts"
		example_output += "\n    --script list [--script-args show='category,author' find=sqlite] \\"
		example_output += "\n    --ext-script <dir-path-to-other-scripts>"
		return example_output

	def _help_info(self):
		help_output  = "  Shows help on how to use the extended script feature."
		help_output += "\n"
		help_output += "\n  Use '-v' to show internal script information (useful for debugging),"
		help_output += "\n  combine with '--script-args' to see how options are parsed."
		help_output += "\n"
		help_output += "\n  This is done through the '--script' argument, combine with '--script-args' to pass"
		help_output += "\n  options to the script."
		help_output += "\n  Use '--script-help <script>' to get help on a specific script."
		help_output += "\n"
		help_output += "\n  Use '-v' to show internal script information (useful for debugging), combine with"
		help_output += "\n  '--script-args' to see how they are rendered."
		help_output += "\n"
		help_output += "\n  Use '-v' to show internal script information (useful for debugging), combine with"
		return help_output