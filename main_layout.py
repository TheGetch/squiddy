import PySimpleGUI as sg

menu_def = [
    [
        "&Project",
        [
            "&New::new_project",
            "&Open::existing_project",
            "&Save::save_project",
            "---",
            "E&xit::exit",
        ],
    ],
    [
        "&Vulnerabilities",
        [
            "&New::new_vuln",
            "&Edit::edit_vuln",
            "---",
            "&Remove::rem_vuln",
        ],
    ],
    [
        "&Attachments",
        [
            "&New::new_attachment",
            "&Edit::edit_attachment",
            "---",
            "&Remove::rem_attachment",
        ],
    ],
    ["&Help", "&About..."],
]

right_click_name = ["", ["Copy::copy_name"]]
right_click_id = ["", ["Copy::copy_id"]]
right_click_url = ["", ["Copy::copy_url", "Open in browser::open_url"]]
right_click_env = ["", ["Copy::copy_env"]]

# Main window
def layout():
    return [
        [sg.Menu(menu_def, tearoff=False, pad=(200, 1))],
        [
            sg.Text("Name", size=(15, 1)),
            sg.Input(
                key="appname", enable_events=True, right_click_menu=right_click_name
            ),
        ],
        [
            sg.Text("ID", size=(15, 1)),
            sg.Input(key="appid", enable_events=True, right_click_menu=right_click_id),
        ],
        [
            sg.Text("URL", size=(15, 1)),
            sg.Input(
                key="appurl", enable_events=True, right_click_menu=right_click_url
            ),
        ],
        [
            sg.Text("Environment", size=(15, 1)),
            sg.Input(
                key="appenv", enable_events=True, right_click_menu=right_click_env
            ),
        ],
        [sg.HorizontalSeparator(pad=(5, 10))],
        [sg.Text("Vulnerabilities", size=(15, 1))],
        [
            sg.Listbox(
                key="vuln_list",
                enable_events=True,
                size=(62, 6),
                values=[],
                expand_y=True,
                select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            ),
        ],
        [sg.Text("Attachments", size=(15, 1))],
        [
            sg.Listbox(
                key="attachment_list",
                enable_events=True,
                size=(62, 6),
                values=[],
                expand_y=True,
                select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            ),
        ],
    ]


def window(ctx):
    return sg.Window(
        "Squiddy",
        layout(),
        icon=ctx.icon(),
        finalize=True,
    )
