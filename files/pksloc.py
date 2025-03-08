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
	locale.installation = Locale()
	locale.installation.start = "Installing package %s!"
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
	if loc == "de_DE":
		pass # example for how to process
	return locale