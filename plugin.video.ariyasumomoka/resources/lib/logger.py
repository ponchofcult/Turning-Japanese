import xbmc
from . import tools

def debug(message):
    
    log_enabled = tools.getSetting("debug")
    
    if log_enabled == "true":
        xbmc.log("ARIYASU MOMOKA: " + str(message) ,xbmc.LOGINFO)