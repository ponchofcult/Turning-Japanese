import xbmcaddon

def getSetting(settingName):
    setting=xbmcaddon.Addon().getSetting(settingName)
    return setting
