"""
Returned when a file was overwritten.
"""
OVERWRITTEN = 102

SUCCESS = 0
FAILURE = -1

"""
Returned when the PKS Format Version is not what is expected.
This is usually bad; because it means that the rest of the .PKS file
  cannot be interpreted with confidence.
"""
OLD_PACKAGE = -100

"""
Returned when a file extension was provided that is not expected or supported.
This only applies to .PKS files for more verbose warnings.
This can happen when packaging a file (output should be .pks) or when installing
  a local package (input should be .pks).
"""
BAD_EXTENSION = -101

"""
Returned when a file already exists.
"""
EXISTS = -102

"""
Returned when a file or key doesn't exist.
"""
MISSING = -103

"""
Returned when the repository name is not configured.
Replaces a KeyError, basically.
"""
REPO_MISSING = -104

"""
Returned when a package is already installed.
"""
ALREADY_INSTALLED = -105

"""
Raised when a provided value to a PKS function is not what it should've been.
eg. MakeTemp("asdf") >> UNEXPECTED
      Why? 'asdf' is not one of the expected values for `purpose`.
"""
class UNEXPECTED(Exception):
	def __init__(self,a):
		super().__init__(a)