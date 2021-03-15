// Copyright (c) 2021 Aldo Hoeben / fieldOfView
// SettingVisibilityProfileCreator is released under the terms of the AGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.3 as UM
import Cura 1.1 as Cura

// Dialog to request a name when creating a new profile
UM.RenameDialog
{
    id: createQualityDialog
    title: catalog.i18nc("@title:window", "Store Custom Setting Visibility Set")
    object: "Custom set"
    onAccepted:
    {
    	manager.createSettingVisibilityPreset(newName)
    }
}
