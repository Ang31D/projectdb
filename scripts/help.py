from Script import Script
import os
from tabulate import tabulate

class init(Script):
	def __init__(self):
		super().__init__()
		self._path = __file__
		self.name = '.'.join(os.path.basename(self._path).split(".")[:-1])
		self.author = "Kim Bokholm"
		self.description = "Shows help on extended script feature"
		# ^-- maybe switch to 'dependencies' instead of 'requirements'
		self._categories.append("help")

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