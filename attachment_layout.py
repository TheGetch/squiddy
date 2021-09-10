import json
import os
import PySimpleGUI as sg

import parse_command


def expando(key):
    return sg.Submit("↗", key=key, tooltip="Expand")


def layout(ctx, attachment, attachment_id, host):
    print("attachment", attachment, attachment_id)
    command = attachment["command"] if attachment and "command" in attachment else ""
    results = attachment["results"] if attachment and "results" in attachment else ""
    attachment_type = (
        attachment["attachment_type"]
        if attachment and "attachment_type" in attachment
        else "*Select attachment type*"
    )

    command = parse_command.parse(command, host)

    attachment_types = ctx.get_attachment_types()
    attachment_types.insert(0, "*Select attachment type*")

    # right_click_menu = ["", ["Copy", "Paste", "Select All", "Cut"]]
    right_click_menu = ["", ["Copy", "Paste", "Select All"]]

    return [
        [
            [
                sg.Input(
                    key="attachment_id_old", default_text=attachment_id, visible=False
                )
            ],
            [
                sg.Text("Name", size=(15, 1)),
                sg.Input(key="attachment_id", default_text=attachment_id),
            ],
            [
                sg.Text("Type", size=(15, 1)),
                sg.Combo(
                    attachment_types,
                    default_value=attachment_type,
                    key="attachment_type",
                    readonly=True,
                    enable_events=True,
                ),
            ],
            [
                sg.Text("Command", size=(15, 1)),
                sg.Input(command, key="command", enable_events=True),
            ],
        ],
        [
            [
                sg.Text("Results", size=(15, 1)),
                sg.Column(
                    [[expando("expand_results")]],
                    element_justification="right",
                    vertical_alignment="bottom",
                    expand_x=True,
                ),
            ],
            [
                sg.Multiline(
                    results,
                    key="results",
                    size=(70, 5),
                    right_click_menu=right_click_menu,
                )
            ],
        ],
        [sg.Submit("Save", key="save")],
    ]


def update_window(window, value, templates_folder, host):
    print(value["attachment_type"], templates_folder)

    command_name = value["attachment_type"].lower()

    template_path = os.path.join(templates_folder, command_name + ".json")
    if not os.path.exists(template_path):
        print("Unable to locate template file")
        return

    template_file = open(template_path, "r")

    data = {}
    try:
        data = json.load(template_file)
    except:
        pass

    command = data["command"] if data and "command" in data else ""

    command = parse_command.parse(command, host)

    window["command"].update(value=command)
    # if not value["attachment_id"]:
    #     window["attachment_id"].update(value=value["attachment_type"])
