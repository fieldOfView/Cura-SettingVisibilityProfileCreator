# Copyright (c) 2019 fieldOfView
# SettingVisibilityProfileCreator is released under the terms of the AGPLv3 or higher.

from configparser import ConfigParser
from collections import OrderedDict
import os.path
import urllib

from PyQt5.QtCore import QObject
from UM.FlameProfiler import pyqtSlot

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
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Store Custom Setting Visibility Set"), self.showNameDialog)

        self._create_profile_window = None

    def showNameDialog(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ProfileNameDialog.qml")
        self._create_profile_window = self._application.createQmlComponent(path, {"manager": self})
        self._create_profile_window.show()

    @pyqtSlot(str)
    def createSettingVisibilitySet(self, set_name):
        global_stack = self._application.getGlobalContainerStack()
        if not global_stack:
            return

        visible_settings = SettingPreferenceVisibilityHandler().getVisible()

        parser = ConfigParser(interpolation = None, allow_no_value = True)  # Accept options without any value
        parser["general"] = {
            "name": set_name,
            "weight": 0
        }

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

        file_name = urllib.parse.quote_plus(set_name)
        with open(os.path.join(storage_path, "%s.cfg" % file_name), 'w') as parser_file:
            parser.write(parser_file)
