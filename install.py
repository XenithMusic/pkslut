import os

print("Installing packslut...")

def Task_AddPath():
	with open("~/.bashrc","a") as f:
		f.write(r"export PATH=$PATH:/home/cookii/.packslut")
def Task_Download():
	temp = os.environ.get("TEMP",os.environ.get("TMPDIR","/var/tmp")).rstrip("/")
	os.makedirs(temp + "/pkslut-install/download",exist_ok=True)
	


tasks = [
Task_Download
# Task_AddPath
]