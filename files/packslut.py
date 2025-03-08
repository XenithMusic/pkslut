import argparse,os
from colors import *
import urllib.request
import struct,shutil
import pkserr

PKS_FORMAT_VERSION = 1
DEBUGGING_ENABLED = True

temp = os.environ.get("TEMP",os.environ.get("TMPDIR","/var/tmp")).rstrip("/")

def MakeTemp(purpose):
	"""
	Creates temporary directories for a specific purpose
	"""
	if not purpose in ["extract","download","pack"]: raise pkserr.UNEXPECTED(f"MakeTemp(purpose); expected extract,download,pack recieved {purpose}")
	try:
		if purpose == "download":
			os.makedirs(f"{temp}/pkslut/download",exist_ok=True)
		if purpose == "extract":
			os.makedirs(f"{temp}/pkslut/extract",exist_ok=True)
		if purpose == "pack":
			os.makedirs(f"{temp}/pkslut/packaging",exist_ok=True)
	except:
		return pkserr.FAILURE
	return 0

def MakeTemps(purposes):
	"""
	Creates temporary directories for several purposes.
	"""
	for purpose in purposes:
		MakeTemp(purpose)

def DestroyTemps():
	"""
	Deletes all of pkslut's temporary directories to save storage space.
	"""
	try:
		shutil.rmtree(f"{temp}/pkslut")
	except:
		pass

def InstallPackageLocal(path:str):
	"""
	Installs a package from a path.

	Assumes the following:
	- Path is a path to a .PKS file

	Parameters:
	- Path: The path to the package to install.

	Returns:
	- Status Code
		See pkserr.py for error codes.
	"""

	MakeTemps(["extract"])

	data = b""
	with open(path,"rb") as f:
		data = f.read(4)
		print(f"{LIGHT_CYAN}{locale.installation.header}{RESET}")
		pkformat = struct.unpack("I",data)[0]
		print(pkformat,PKS_FORMAT_VERSION)
		if pkformat != PKS_FORMAT_VERSION:
			return pkserr.OLD_PACKAGE
		data = f.read(4)
		pknamelength = struct.unpack("I",data)[0]
		pkname = b""
		for i in range(pknamelength):
			data = f.read(1)
			pkname += struct.unpack("c",data)[0]
		data = f.read(4)
		pkversion = tuple(struct.unpack("BBH",data))
		data = f.read()
		remainder = data.split(b"\x00")
		print(f"{LIGHT_CYAN}{locale.installation.compat}{RESET}")
		compat = remainder[0]
		print(f"{LIGHT_CYAN}{locale.installation.script}{RESET}")
		script = remainder[1]
		print(f"{LIGHT_CYAN}{locale.installation.archive}{RESET}")
		archive = b"\x00".join(remainder[2:])
	print(f"{LIGHT_CYAN}{locale.installation.environment}{RESET}")
	with open(f"{temp}/pkslut/extract/archive.zip","wb") as f:
		f.write(archive)
	os.system(f"unzip {temp}/pkslut/extract/archive.zip -d {temp}/pkslut/extract/archive")
	with open(f"{temp}/pkslut/extract/archive/INSTALL.sh","wb") as f:
		f.write(script)
	with open(f"{temp}/pkslut/extract/archive/COMPATIBILITY.txt","wb") as f:
		f.write(compat)
	print(f"{LIGHT_CYAN}{locale.installation.execute}{RESET}")
	os.system(f"chmod +x {temp}/pkslut/extract/archive/INSTALL.sh")
	os.system(f"{temp}/pkslut/extract/archive/INSTALL.sh")
	return pkserr.SUCCESS

def InstallPackageURL(url:str,name:str):
	"""
	Installs a package from a URL.

	Assumes the following:
	- URL is a link to a .PKS file

	Parameters:
	- URL: The URL to download from
	- Name: What to name the locally downloaded package. (not including .pks)

	Returns:
	- Status Code
		See pkserr.py for error codes.
	"""

	MakeTemps(["download"])

	print(f"{LIGHT_CYAN}{locale.installation.downloadURL}{RESET}" % (name,url))

	urllib.request.urlretrieve(url,f"{temp}/pkslut/download/{name}.pks")
	InstallPackageLocal(f"{temp}/pkslut/download/{name}.pks")

	return pkserr.SUCCESS

def MakePackage(pkname,_pkversion,assets,output):
	"""
	Creates a new .PKS package.

	Parameters:
	- Package Name
		eg. "git" for git
	- Package Version
		eg. "1.0.0" for version 1.0.0
	- Compatibility File
	- Assets Folder (**MUST** contain INSTALL.sh and COMPATIBILITY.txt)

	Returns:
	- Status Code
	"""

	MakeTemps(["pack"])

	# Preprocessing
	if not output.endswith(".pks"):
		return pkserr.BAD_EXTENSION
	pkversion = [int(x) for x in _pkversion.split(".")[:3]]
	print(pkversion)

	# Create Package
	print(f"{LIGHT_CYAN}- {locale.packaging.header}{RESET}") # Encoding header...
	data = b""
	data += struct.pack("I",PKS_FORMAT_VERSION)
	data += struct.pack("I",len(pkname))
	for i in bytes(pkname,"UTF-8"):
		# Repacking like this because for some reason b"abc" does not always pack efficiently.
		# Absolutely zero clue why. Might just be going crazy.
		data += struct.pack("B",i)
	data += struct.pack("BBH",pkversion[0],pkversion[1],pkversion[2])

	# Pack the compatibility section
	print(f"{LIGHT_CYAN}- {locale.packaging.compat}{RESET}") # Encoding compatibility information...
	with open(assets.rstrip("/") + "/COMPATIBILITY.txt","rb") as f:
		data += f.read()
	data += struct.pack("B",0)

	# Pack the script
	print(f"{LIGHT_CYAN}- {locale.packaging.script}{RESET}") # Encoding install script...
	with open(assets.rstrip("/") + "/INSTALL.sh","rb") as f:
		data += f.read()
	data += struct.pack("B",0)

	try:
		shutil.rmtree(f"{temp}/pkslut/packaging/PACKAGE_ASSETS")
	except FileNotFoundError as e:
		pass
	shutil.copytree(assets,f"{temp}/pkslut/packaging/PACKAGE_ASSETS")
	for i in [
			f"{temp}/pkslut/packaging/PACKAGE_ASSETS/INSTALL.sh",
			f"{temp}/pkslut/packaging/PACKAGE_ASSETS/COMPATIBILITY.txt"]:

		try:
			os.remove(i)
		except:
			pass

	# Pack the archive.
	print(f"{LIGHT_CYAN}- {locale.packaging.archive}{RESET}") # Encoding archive...
	os.system(f"""cd {temp}/pkslut/packaging/PACKAGE_ASSETS && \
zip -r {temp}/pkslut/packaging/archive.zip ./*""")
	print(os.listdir(f"{temp}/pkslut/packaging"))
	with open(f"{temp}/pkslut/packaging/archive.zip","rb") as f:
		data += f.read()

	# Create .PKS
	print(f"{LIGHT_CYAN}- {locale.packaging.emit}{RESET}") # Emitting package...
	if os.path.exists(output):
		print(f"{ORANGE}{locale.packaging.warning}{RESET}" % locale.errors[pkserr.OVERWRITTEN])
	with open(output,"wb") as f:
		f.write(data)

	return pkserr.SUCCESS

def invoke():
	global locale
	from pksconf import Config
	from pksloc import generateTexts
	config = Config()
	if DEBUGGING_ENABLED:
		print(f"{LIGHT_RED}Debugging is enabled!\n")
		print(f"If you see this in a production release, please notify cookiiq at <xenith.contact.mail@gmail.com>{RESET}")
	ap = argparse.ArgumentParser(
		prog="packslut",
		description="A package manager made for fun~.",
		add_help=False)
	pos = ap.add_argument_group("Positional Arguments")
	subparsers = ap.add_subparsers(title="Modes",metavar="{ install, remove, info, ... }")
	subparsers.add_parser("install",
		help="Install a package.",)

	subparsers.add_parser("remove",
		help="Remove a package.",)

	subparsers.add_parser("info",
		help="Fetch information about a package.",)

	md_pack = subparsers.add_parser("pack",
		help="Create a new .PKS file which can then be pushed onto a repository.",)
	md_pack.set_defaults(mode="pack")
	md_pack.add_argument("name",
		help="The name of the package to build.")
	md_pack.add_argument("version",
		help="The version of the package to build.")
	md_pack.add_argument("package",
		help="Target directory to make a .PKS from.")
	md_pack.add_argument("-o","--output",
		help="Where to place the .PKS file",
		default=None)

	md_local = subparsers.add_parser("local",
		help="Install a local .pks file.")
	md_local.set_defaults(mode="local")
	md_local.add_argument("package",
		help="Target directory to make a .PKS from.")

	md_repo = subparsers.add_parser("rm-repo",
		help="Removes a repository.")
	md_repo.set_defaults(mode="rm-repo")
	md_repo.add_argument("name",
		help="Name of the repository")

	md_repo = subparsers.add_parser("add-repo",
		help="Adds a repository.")
	md_repo.set_defaults(mode="add-repo")
	md_repo.add_argument("name",
		help="Name of the repository")
	md_repo.add_argument("link",
		help="Link to the directory containing all packages.")
	# https://github.com/XenithMusic/pkslut-repo/raw/refs/heads/master/demoPackage.pks

	installopts = ap.add_argument_group("Install options")
	installopts.add_argument("-r","--repo",
		help="Uses a specific repository instead of the default.",
		metavar="REPOSITORY")

	opts = ap.add_argument_group("Global options")
	opts.add_argument("-h","--help",
		help="Show this message, then exit.",
		action="help")

	args = ap.parse_args()

	locale = generateTexts("en_US")

	print(args)
	match args.mode:
		case "pack":
			print(f"{GREEN}{locale.packaging.start}{RESET}" % (args.name,args.version,args.package))
			a = MakePackage(args.name,args.version,args.package,args.output or (args.name + ".pks"))
			if a >= 0:
				print(f"{GREEN}{locale.packaging.success}{RESET}" % args.name)
			elif a < 0:
				print(f"{RED}{locale.packaging.failure}{RESET}" % (args.name,locale.errors[a]))
		case "local":
			print(f"{GREEN}{locale.installation.start}{RESET}" % args.package)
			a = InstallPackageLocal(args.package)
			if a >= 0:
				print(f"{GREEN}{locale.installation.success}{RESET}")
			elif a < 0:
				print(f"{RED}{locale.installation.failure}{RESET}" % locale.errors[a])
		case "add-repo":
			print(f"{GREEN}{locale.repository.adding}{RESET}" % (args.name,args.link))

			# HACK: config["repositories"][args.name]
			#		the above does NOT call __setitem__
			#		SO, i have to do it manually as I've
			#		done below. Python moment!
			a = config["repositories"]
			a[args.name] = args.link
			config["repositories"] = a

	if DEBUGGING_ENABLED:
		print(f"{LIGHT_RED}Breaking before temp dir cleanup for inspection.\n")
		print(f"Run 'c' in PDB to exit.{RESET}")
		breakpoint()
	DestroyTemps()
if __name__ == '__main__':
	invoke()