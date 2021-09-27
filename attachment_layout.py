import json
import os
import PySimpleGUI as sg

import parse_command

menu_def = [
    [
        "&Attachment",
        [
            "&Save::save_attachment",
        ],
    ],
    ["&Additional Info", ["&ExplainShell::explain"]],
]


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
    if attachment_types[0] != "*Select attachment type*":
        attachment_types.insert(0, "*Select attachment type*")

    # right_click_menu = ["", ["Copy", "Paste", "Select All", "Cut"]]
    right_click_menu = ["", ["Copy", "Paste", "Select All"]]

    return [
        [sg.Menu(menu_def, tearoff=False, pad=(200, 1))],
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
            ],
            [
                sg.Multiline(
                    results,
                    key="results",
                    size=(70, 5),
                    right_click_menu=right_click_menu,
                    expand_x=True,
                    expand_y=True,
                )
            ],
        ],
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


def window(ctx, attachment, attachment_id):
    layout_attachment = layout(ctx, attachment, attachment_id, ctx.app_url)
    return sg.Window(
        "Squiddy - Attachment",
        layout_attachment,
        icon=ctx.icon(),
        finalize=True,
        resizable=True,
    )
