# Copyright (c) 2021 Aldo Hoeben / fieldOfView
# SettingVisibilityProfileCreator is released under the terms of the AGPLv3 or higher.

from . import SettingVisibilityProfileCreator

def getMetaData():
    return {}

def register(app):
    return {"extension": SettingVisibilityProfileCreator.SettingVisibilityProfileCreator()}
