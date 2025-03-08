import argparse,os
from colors import *
import urllib.request
import struct,shutil
import pkserr

PKS_FORMAT_VERSION = 2
"""
PKS changelog:
v1: Initial
v2: Add Repository Identification
	+ Repository Identifier.
		COMPATIBILITY is now in the format:
		`PackageName:Repository:>=VERSION`
		instead of
		`PackageName:>=VERSION`
"""

def sys(x):
	print(f"{LIGHT_RED}>>> {RESET}{x}")
	os.system(x)

DEBUGGING_ENABLED = False

temp = os.environ.get("TEMP",os.environ.get("TMPDIR","/var/tmp")).rstrip("/")
home = os.environ.get('HOME').rstrip("/")

def verifyOperation(default="y"):
	a,b = "Y","n"
	if default.lower() == "n": a,b = "y","N"
	pick = input(f"{ORANGE}{locale.verify}{YELLOW}" % (a,b))
	print(f"{RESET}",end="")
	if pick.lower() in ["y","n"]:
		return pick.lower() == "y"
	else:
		return default

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
	strpkname = pkname.decode("UTF-8")
	print(f"{LIGHT_CYAN}{locale.installation.environment}{RESET}")
	os.makedirs(f"{home}/.pkslut-packages/{strpkname}")
	with open(f"{temp}/pkslut/extract/archive.zip","wb") as f:
		f.write(archive)
	sys(f"unzip {temp}/pkslut/extract/archive.zip -d {home}/.pkslut-packages/{strpkname}")
	with open(f"{home}/.pkslut-packages/{strpkname}/INSTALL.sh","wb") as f:
		f.write(script)
	with open(f"{home}/.pkslut-packages/{strpkname}/COMPATIBILITY.txt","wb") as f:
		f.write(compat)
	print(f"{LIGHT_CYAN}{locale.installation.execute}{RESET}")
	sys(f"chmod +x {home}/.pkslut-packages/{strpkname}/INSTALL.sh")
	sys(f"{home}/.pkslut-packages/{strpkname}/INSTALL.sh")
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

	if name in os.listdir(f"{home}/.pkslut-packages"):
		return pkserr.ALREADY_INSTALLED

	MakeTemps(["download"])

	print(f"{LIGHT_CYAN}{locale.installation.downloadURL}{RESET}" % (name,url))

	urllib.request.urlretrieve(url,f"{temp}/pkslut/download/{name}.pks")
	return InstallPackageLocal(f"{temp}/pkslut/download/{name}.pks")

def InstallPackageRepo(name:str,repo:str):
	global config
	"""
	Installs a package from a configured repository.

	Assumes the following:
	- Repo is a valid key in Config["repositories"]
	- Repo links to a branch head
	- Name is a valid package in said branch

	Parameters:
	- Package File Name
	- Repository Name

	Returns:
	- Status Code
		See pkserr.py for error codes.
	"""

	if repo in config["repositories"]:
		link = config["repositories"][repo].rstrip("/") + f"/{name}.pks"
		return InstallPackageURL(link,name)
	else:
		return pkserr.REPO_MISSING

def RemovePackage(name:str):
	"""
	Uninstalls a installed package.

	Parameters:
	- Package Name

	Returns:
	- Status Code
		See pkserr.py for error codes.
	"""

	if ".." in name:
		return pkserr.UNSAFE

	shutil.rmtree(f"{home}/.pkslut-packages/{name}")
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
		See pkserr.py for error codes.
	"""

	if ".." in pkname:
		return pkserr.UNSAFE

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
	sys(f"""cd {temp}/pkslut/packaging/PACKAGE_ASSETS && \
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
	global locale,config
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
	md_install = subparsers.add_parser("install",
		help="Install a package from a configured repository.",)
	md_install.set_defaults(mode="install")
	md_install.add_argument("package",
		help="Target package to install.")
	md_install.add_argument("-r","--repo",
		help="Uses a specific repository instead of the default.",
		metavar="REPOSITORY",
		default=config["defaultRepo"])

	md_reinstall = subparsers.add_parser("reinstall",
		help="Reinstall a package.",)
	md_reinstall.set_defaults(mode="reinstall")
	md_reinstall.add_argument("package",
		help="Target package to reinstall.")
	md_reinstall.add_argument("-r","--repo",
		help="Target repo to reinstall from.",
		default=config["defaultRepo"])

	md_remove = subparsers.add_parser("remove",
		help="Remove a package.",)
	md_remove.set_defaults(mode="remove")
	md_remove.add_argument("package",
		help="Target package to remove.")

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

	md_rrepo = subparsers.add_parser("rm-repo",
		help="Removes a repository.")
	md_rrepo.set_defaults(mode="rm-repo")
	md_rrepo.add_argument("name",
		help="Name of the repository")

	md_arepo = subparsers.add_parser("add-repo",
		help="Adds a repository.")
	md_arepo.set_defaults(mode="add-repo")
	md_arepo.add_argument("name",
		help="Name of the repository")
	md_arepo.add_argument("link",
		help="Link to the directory containing all packages.")
	# https://github.com/XenithMusic/pkslut-repo/raw/refs/heads/master/demoPackage.pks

	opts = ap.add_argument_group("Global options")
	opts.add_argument("-h","--help",
		help="Show this message, then exit.",
		action="help")

	args = ap.parse_args()

	locale = generateTexts("en_US")

	print(args)
	match args.mode:
		case "reinstall":
			print(f"{GREEN}{locale.reinstall.start}{RESET}" % (args.package))
			a = RemovePackage(args.package)
			if a >= 0:
				a = InstallPackageRepo(args.package,args.repo)
				if a >= 0:
					print(f"{GREEN}{locale.reinstall.success}{RESET}" % args.package)
				elif a < 0:
					print(f"{RED}{locale.reinstall.failure}{RESET}" % (args.package,locale.errors[a]))
			elif a < 0:
				print(f"{RED}{locale.reinstall.failure}{RESET}" % (args.package,locale.errors[a]))
		case "remove":
			if verifyOperation():
				print(f"{GREEN}{locale.removal.start}{RESET}" % (args.package))
				a = RemovePackage(args.package)
				if a >= 0:
					print(f"{GREEN}{locale.packaging.success}{RESET}" % args.package)
				elif a < 0:
					print(f"{RED}{locale.packaging.failure}{RESET}" % (args.package,locale.errors[a]))
			else:
				print(f"{RED}{locale.cancelled}{RESET}")
		case "install":
			if verifyOperation():
				print(f"{GREEN}{locale.installation.startRepo}{RESET}" % (args.package,args.repo))
				a = InstallPackageRepo(args.package,args.repo)
				if a >= 0:
					print(f"{GREEN}{locale.installation.successname}{RESET}" % args.package)
				elif a < 0:
					print(f"{RED}{locale.installation.failurename}{RESET}" % (args.package,locale.errors[a]))
			else:
				print(f"{RED}{locale.cancelled}{RESET}")
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
			try:
				a = config["repositories"]
				a[args.name] = args.link
				config["repositories"] = a
				print(f"{GREEN}{locale.repository.added}{RESET}" % (args.name,args.link))
			except Exception as e:
				print(f"{RED}{locale.repository.failure}{RESET}" % (""))
				raise e
		case "rm-repo":
			print(f"{GREEN}{locale.repository.removing}{RESET}" % (args.name))

			# HACK: config["repositories"][args.name]
			#		the above does NOT call __setitem__
			#		SO, i have to do it manually as I've
			#		done below. Python moment!
			try:
				a = config["repositories"]
				del a[args.name]
				config["repositories"] = a
				print(f"{GREEN}{locale.repository.removed}{RESET}" % (args.name))
			except Exception as e:
				print(f"{RED}{locale.repository.failure}{RESET}" % (""))
				raise e

	if DEBUGGING_ENABLED:
		print(f"{LIGHT_RED}Breaking before temp dir cleanup for inspection.\n")
		print(f"Run 'c' in PDB to exit.{RESET}")
		breakpoint()
	DestroyTemps()
if __name__ == '__main__':
	invoke()