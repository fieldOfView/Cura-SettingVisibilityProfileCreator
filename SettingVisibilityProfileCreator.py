# Copyright (c) 2022 Aldo Hoeben / fieldOfView
# SettingVisibilityProfileCreator is released under the terms of the AGPLv3 or higher.

from configparser import ConfigParser
from collections import OrderedDict
import os.path
import urllib

try:
    from PyQt6.QtCore import QObject
except ImportError:
    from PyQt5.QtCore import QObject
from UM.FlameProfiler import pyqtSlot

from cura.CuraApplication import CuraApplication

from UM.Extension import Extension
from UM.Logger import Logger
from UM.Resources import Resources
from UM.Version import Version

from UM.Settings.ContainerRegistry import ContainerRegistry
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.Models.SettingPreferenceVisibilityHandler import SettingPreferenceVisibilityHandler
try:
    from cura.Settings.SettingVisibilityPreset import SettingVisibilityPreset
except ImportError:
    SettingVisibilityPreset = None  # type: ignore

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")


class SettingVisibilityProfileCreator(Extension, QObject,):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        Extension.__init__(self)

        if SettingVisibilityPreset == None:
            # Cura 3.5
            Logger.log("e", "The plugin is not compatible with this version of Cura")
            return

        self._application = CuraApplication.getInstance()

        try:
            use_controls1 = False
            if self._application.getAPIVersion() < Version(8) and self._application.getVersion() != "master":
                use_controls1 = True
        except AttributeError:
             # UM.Application.getAPIVersion was added for API > 6 (Cura 4)
            use_controls1 = True
        self._qml_folder = "qml" if not use_controls1 else "qml_controls1"

        self.setMenuName(catalog.i18nc("@item:inmenu", "Setting Visibility Sets"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Store Customised Setting Visibility Set"), self.showNameDialog)

        self._create_profile_window = None

    def showNameDialog(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self._qml_folder, "ProfileNameDialog.qml")
        self._create_profile_window = self._application.createQmlComponent(path, {"manager": self})
        self._create_profile_window.show()

    @pyqtSlot(str)
    def createSettingVisibilityPreset(self, preset_name):
        global_stack = self._application.getGlobalContainerStack()
        if not global_stack:
            return

        preset_id = preset_name.lower()
        new_preset = SettingVisibilityPreset(preset_id = preset_id, name = preset_name)

        version = 1
        try:
            if self._application.getAPIVersion() >= Version("7.5.0"):
                version = 2
        except AttributeError:
            # Applocation.getAPIVersion() was introduced in Cura 4.0
            # version should be 1 in these old versions of Cura
            pass

        parser = ConfigParser(interpolation = None, allow_no_value = True)  # Accept options without any value
        parser["general"] = {
            "name": new_preset.name,
            "weight": new_preset.weight,
            "version": version
        }

        visible_settings = SettingPreferenceVisibilityHandler().getVisible()

        settings = []
        exclude = set(["machine_settings", "command_line_settings"])
        category = ""
        for setting in global_stack.definition.findDefinitions():
            if setting.key in exclude or setting.getAncestors() & exclude:
                continue

            if setting.type == "category":
                category = setting.key
                parser[category] = OrderedDict()
                settings.append(setting.key)
            elif setting.key in visible_settings:
                parser[category][setting.key] = None
                settings.append(setting.key)

        new_preset.setSettings(settings)

        storage_path = Resources.getStoragePath(CuraApplication.ResourceTypes.SettingVisibilityPreset)

        file_name = "%s.cfg" % urllib.parse.quote_plus(preset_id)
        with open(os.path.join(storage_path, file_name), 'w') as parser_file:
            parser.write(parser_file)

        presets_model = self._application.getSettingVisibilityPresetsModel()
        # Remove preset with the same name, if any
        items = [item for item in presets_model.items if item.presetId != preset_id]
        items.append(new_preset)
        # Sort them on weight (and if that fails, use ID)
        items.sort(key = lambda k: (int(k.weight), k.presetId))

        presets_model.setItems(items)
        presets_model.setActivePreset(preset_id)
