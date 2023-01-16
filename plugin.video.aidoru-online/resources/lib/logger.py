import xbmc
from . import tools

def debug(message):
    
    log_enabled = tools.getSetting("debug")
    
    if log_enabled == "true":
        xbmc.log("TEST ADDON: " + str(message) ,xbmc.LOGINFO)