import os
home = os.environ.get('HOME').rstrip("/")
temp = os.environ.get("TEMP",os.environ.get("TMPDIR","/var/tmp")).rstrip("/")

def getFn(x):
	import ast
	if x == "int": return int
	if x == "str": return str
	if x == "chrs": return list # because list("[1]") == ["[","1","]"] for some reason
	if x == "bool": return bool
	if x == "eval": return ast.literal_eval

	raise KeyError(f"Expected int/str/chrs/bool/eval, got {x}")

def fromType(x):
	t = type(x)
	# if t == int: return "int"
	# if t == str: return "str"
	# if t == list and len([i for i in x if len(i) != 1]) == 0: return "chrs"
	# if t == bool: return bool
	return "eval"

class Config:
	def __init__(self):
		self.loadConfig()
	def saveConfig(self):
		global CONFIG
		CONFIG = [k+":"+fromType(v)+":"+repr(v) for k,v in CONFIG.items()]
		print(CONFIG)
		CONFIG = "\n".join(CONFIG)
		print(CONFIG)
		with open(f"{home}/.config/packslut/config","w") as f:
			f.write(CONFIG)

	def loadConfig(self):
		global CONFIG
		with open(f"{home}/.config/packslut/config","r") as f:
			CONFIG = f.read()
		if CONFIG == "default":
			CONFIG = """# This is an automatically generated configuration file.
repositories:eval:{"pks":"https://github.com/XenithMusic/pkslut-repo/raw/refs/heads/master/"}
defaultRepo:str:pks"""
			with open(f"{home}/.config/packslut/config","w") as f:
				f.write(CONFIG)
		CONFIG = CONFIG.split("\n")
		CONFIG = [x.lstrip().split(":") for x in CONFIG if not x.startswith("#")]
		CONFIG = {x[0]:getFn(x[1])(":".join(x[2:])) for x in CONFIG if len(x) >= 3}
	def __getitem__(self,key):
		return CONFIG[key]
	def __setitem__(self,key,value):
		CONFIG[key] = value
		self.saveConfig()