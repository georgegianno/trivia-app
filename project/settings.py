# This is just a representation of how a production file could be. The settings_local.py does not exist in repo,
# and is created with the make sync_settings command in Makefile. We create a file that should not be in 
# production server via simlink, to only test locally. 
try:
    from .settings_local import *
except:
    from .production_settings import *