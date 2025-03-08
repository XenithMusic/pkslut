import os,shutil
import platform
import argparse
import urllib.request

def Task_Prerequesites():
	if platform.system() == "Windows":
		raise OSError("Windows is not supported.")
	if platform.system() == "Darwin":
		raise OSError("MacOS, iOS, and iPadOS are not supported.")
	if platform.system() == "Java":
		raise RuntimeError("You are using Jython, and for some reason, that returns Java for platform.system. Could not determine operating system.")
def Task_Preinstall():
	global temp,home
	home = os.environ.get('HOME').rstrip("/")
	temp = os.environ.get("TEMP",os.environ.get("TMPDIR","/var/tmp")).rstrip("/")
	print("- Uninstalling any previous installations...")
	try:
		shutil.rmtree(f"{temp}/pkslut-install")
	except FileNotFoundError:
		pass
	try:
		shutil.rmtree(f"{home}/.local/share/packslut")
	except FileNotFoundError:
		pass
	lines = []
	with open(f"{home}/.bashrc","r") as f:
		lines = f.read().split("\n")
	f = {
		"export PATH=$PATH:/home/cookii/.local/share/packslut",
		"export PATH=$PATH:/home/cookii/.pkslut-packages",
	}
	lines = [line for line in lines if not line.strip() in f]
	with open(f"{home}/.bashrc","w") as f:
		f.write("\n".join(lines))
def Task_Setup():
	# Temporary Files for install
	os.makedirs(f"{temp}/pkslut-install/download/extract",exist_ok=True)

	# Packslut data
	os.makedirs(f"{home}/.local/share/packslut",exist_ok=True)
	# Packslut configuration
	os.makedirs(f"{home}/.config/packslut",exist_ok=True)
	with open(f"{home}/.config/packslut/config","w") as f:
		f.write("default")
	# Installed package storage
	os.makedirs(f"{home}/.pkslut-packages",exist_ok=True)
def Task_Download():
	latest = "https://github.com/XenithMusic/pkslut/zipball/master"
	urllib.request.urlretrieve(latest,f"{temp}/pkslut-install/download/LATEST.zip")
def Task_Extract():
	dn_extract = f"{temp}/pkslut-install/download/extract/"
	ex_extract = f"{temp}/pkslut-install/extract/"
	os.system(f"unzip {temp}/pkslut-install/download/LATEST.zip -d {dn_extract}")
	os.rename(dn_extract + os.listdir(dn_extract)[0],ex_extract)
def Task_Relocate():
	if not "files" in os.listdir(f"{temp}/pkslut-install/extract"):
		raise FileNotFoundError("Expected files in pkslut files.")
	extract = f"{temp}/pkslut-install/extract/files"
	os.rename(extract,f"{home}/.local/share/packslut")
def Task_GenerateShell():
	directory = f"{home}/.local/share/packslut"
	aliases = [f"{directory}/packslut",f"{directory}/pkslut"]
	for i in aliases:
		with open(i,"w") as f:
			f.write(f"""#!/bin/bash
python {directory}/packslut.py \"$@\"""")
		os.system(f"chmod +x {i}")
def Task_AddPath():
	with open(f"{home}/.bashrc","a") as f:
		f.write(f"\nexport PATH=$PATH:{home}/.local/share/packslut\n")
		f.write(f"export PATH=$PATH:{home}/.pkslut-packages")
def Task_Clean():
	shutil.rmtree(f"{temp}/pkslut-install")




def Alt_DownloadLocal():
	os.makedirs(f"{temp}/pkslut-install/extract/",exist_ok=True)
	shutil.copytree("files",f"{temp}/pkslut-install/extract/files")

ap = argparse.ArgumentParser(
	prog="install.py",
	description="The installer for pkSLUT")

ap.add_argument("-l","--local",
	help="Install from a folder named files in the CWD instead of downloading.",
	action="store_true")
ap.add_argument("-d","--dirty",
	help="Don't clean up after self.",
	action="store_true")

args = ap.parse_args()

tasks = [
	Task_Prerequesites,
	Task_Preinstall,
	Task_Setup
]

if args.local:
	tasks += [
		Alt_DownloadLocal,
	]
else:
	tasks += [
		Task_Download,
		Task_Extract
	]

tasks += [
	Task_Relocate,
	Task_GenerateShell,
	Task_AddPath,
]
if not args.dirty:
	tasks += [Task_Clean]

print("Installing packslut...")
for i,v in enumerate(tasks):
	print(f"({i+1}/{len(tasks)}) Running task '{v.__name__}'")
	v()
print("Installation complete! Invoke packslut with the `packslut` command, or the `pkslut` alias.")