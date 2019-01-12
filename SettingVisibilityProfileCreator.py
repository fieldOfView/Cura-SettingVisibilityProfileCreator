# Copyright (c) 2019 fieldOfView
# SettingVisibilityProfileCreator is released under the terms of the AGPLv3 or higher.

from configparser import ConfigParser
from collections import OrderedDict
import os.path

from PyQt5.QtCore import QObject

from cura.CuraApplication import CuraApplication

from UM.Extension import Extension
from UM.Logger import Logger
from UM.Resources import Resources

from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.Models.SettingPreferenceVisibilityHandler import SettingPreferenceVisibilityHandler

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")


class SettingVisibilityProfileCreator(Extension, QObject,):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        Extension.__init__(self)

        self._application = CuraApplication.getInstance()

        self.setMenuName(catalog.i18nc("@item:inmenu", "Setting Visibility Sets"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Store Custom Setting Visibility Set"), self.createSettingVisibilitySet)

    def createSettingVisibilitySet(self):
        global_stack = self._application.getGlobalContainerStack()
        if not global_stack:
            return

        visible_settings = SettingPreferenceVisibilityHandler().getVisible()

        parser = ConfigParser(interpolation = None, allow_no_value = True)  # Accept options without any value
        parser["general"] = {"name": "Custom"}

        exclude = set(["machine_settings", "command_line_settings"])
        category = ""
        for setting in global_stack.definition.findDefinitions():
            if setting.key in exclude or setting.getAncestors() & exclude:
                continue

            if setting.type == "category":
                category = setting.key
                parser[category] = OrderedDict()
            elif setting.key in visible_settings:
                parser[category][setting.key] = None

        storage_path = Resources.getStoragePath(CuraApplication.ResourceTypes.SettingVisibilityPreset)
        print(os.path.join(storage_path, "custom.cfg"))

        #with open('custom.cfg', 'w') as parser_file:
        #    parser.write(parser_file)
