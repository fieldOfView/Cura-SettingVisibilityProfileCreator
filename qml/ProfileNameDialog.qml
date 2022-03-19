// Copyright (c) 2019 Ultimaker B.V.
// Copyright (c) 2021 Aldo Hoeben / fieldOfView
// Uranium is released under the terms of the LGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 2.0
import QtQuick.Window 2.1

import UM 1.5 as UM
import Cura 1.0 as Cura

UM.Dialog
{
    id: base

    function setName(new_name) {
        nameField.text = new_name;
        nameField.selectAll();
        nameField.forceActiveFocus();
    }

    buttonSpacing: UM.Theme.getSize("default_margin").width

    title: catalog.i18nc("@title:window", "Store Custom Setting Visibility Set")

    minimumWidth: UM.Theme.getSize("small_popup_dialog").width
    minimumHeight: UM.Theme.getSize("small_popup_dialog").height
    width: minimumWidth
    height: minimumHeight

    property variant catalog: UM.I18nCatalog { name: "uranium" }

    onVisibleChanged:
    {
        nameField.selectAll();
        nameField.forceActiveFocus();
    }

    onAccepted:
    {
        manager.createSettingVisibilityPreset(nameField.text)
    }

    Column
    {
        anchors.fill: parent

        UM.Label
        {
            text: catalog.i18nc("@info", "Please provide a name. If you use a name of an existing custom set, it will be overwritten.") + "\n" //Newline to make some space using system theming.
            width: parent.width
            wrapMode: Text.WordWrap
        }

        Cura.TextField
        {
            id: nameField
            width: parent.width
            text: catalog.i18nc("@visibility_set title", "Custom set")
            maximumLength: 40
        }
    }

    rightButtons: [
        Cura.SecondaryButton
        {
            id: cancelButton
            text: catalog.i18nc("@action:button","Cancel")
            onClicked: base.reject()
        },
        Cura.PrimaryButton
        {
            id: okButton
            text: catalog.i18nc("@action:button", "OK")
            onClicked: base.accept()
        }
    ]
}

