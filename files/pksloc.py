class Locale:
	def __init__(self):
		pass
	def __getitem__(self,key):
		return getattr(self,repr(key))
	def __setitem__(self, key, value):
		setattr(self, repr(key), value)

def generateTexts(loc):
	locale = Locale()

	# en_US ; default
	locale.packaging = Locale()
	locale.packaging.start = "Creating package %s==%s from %s!"
	locale.packaging.header = "Encoding header..."
	locale.packaging.compat = "Encoding compatibility information..."
	locale.packaging.script = "Encoding install script..."
	locale.packaging.archive = "Encoding archive..."
	locale.packaging.emit = "Emitting package..."
	locale.packaging.success = "Successfully created package %s!"
	locale.packaging.failure = "Failed to create package %s!\nError: %s"
	locale.packaging.warning = "Warning during package creation: %s"
	locale.errors = Locale()
	# Warnings
	locale.errors[102] = "Overwrote a file."
	# Generic
	locale.errors[0] = "Success"
	locale.errors[-1] = "Failure"
	# Errors
	locale.errors[-100] = "PKS file is too new/old."
	locale.errors[-101] = "Expected a .PKS extension."
	locale.errors[-102] = "File already exists."
	locale.errors[-103] = "File does not exist."
	locale.errors[-104] = "Repository does not exist."
	locale.errors[-105] = "Package is already installed."
	locale.errors[-106] = "Not safe to proceed."
	locale.installation = Locale()
	locale.installation.start = "Installing package %s!"
	locale.installation.startRepo = "Installing package %s from %s!"
	locale.installation.downloadURL = "Downloading package %s from %s."
	locale.installation.header = "Extracting header from package..."
	locale.installation.compat = "Extracting compatibility information from package..."
	locale.installation.script = "Extracting script from package..."
	locale.installation.archive = "Extracting archive from package..."
	locale.installation.environment = "Creating installation environment..."
	locale.installation.execute = "Running installation script..."
	locale.installation.successname = "Installed package %s successfully!"
	locale.installation.success = "Installed package successfully!"
	locale.installation.failurename = "Failed to install package %s!\nError: %s"
	locale.installation.failure = "Failed to install package!\nError: %s"
	locale.repository = Locale()
	locale.repository.adding = "Adding repository %s @ %s..."
	locale.repository.added = "Successfully added repository %s @ %s..."
	locale.repository.removing = "Removing repository %s..."
	locale.repository.removed = "Successfully removed repository %s..."
	locale.repository.failure = "Failed to change repositories!\nError: %s"
	locale.removal = Locale()
	locale.removal.start = "Removing package %s..."
	locale.removal.success = "Successfully removed package %s!"
	locale.removal.failure = "Failed to remove package %s!\nError: %s"
	locale.reinstall = Locale()
	locale.reinstall.start = "Reinstalling package %s..."
	locale.reinstall.success = "Successfully reinstalled package %s!"
	locale.reinstall.failure = "Failed to reinstall package %s!\nError: %s"
	locale.verify = "Do you want to continue? [%s/%s]: "
	locale.cancelled = "Operation cancelled by user."
	if loc == "de_DE":
		pass # example for how to process
	return locale