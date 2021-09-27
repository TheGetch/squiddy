import PySimpleGUI as sg

menu_def = [
    [
        "&Project",
        [
            "&New::new_project",
            "&Open::existing_project",
            "&Save::save_project",
            "E&xit::KeyExit",
        ],
    ],
    [
        "&Vulnerability",
        [
            "&New::new_vuln",
            "&Edit::edit_vuln",
            "&Remove::rem_vuln",
        ],
    ],
    [
        "&Attachment",
        [
            "&New::new_attachment",
            "&Edit::edit_attachment",
            "&Remove::rem_attachment",
        ],
    ],
    ["&Help", "&About..."],
]

# Main window
def layout(right_click_url):
    return [
        [sg.Menu(menu_def, tearoff=False, pad=(200, 1))],
        [sg.Text("Name", size=(15, 1)), sg.Input(key="appname", enable_events=True)],
        [sg.Text("ID", size=(15, 1)), sg.Input(key="appid", enable_events=True)],
        [
            sg.Text("URL", size=(15, 1)),
            sg.Input(
                key="appurl", enable_events=True, right_click_menu=right_click_url
            ),
        ],
        [
            sg.Text("Environment", size=(15, 1)),
            sg.Input(key="appenv", enable_events=True),
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


def window(ctx, right_click_url):
    return sg.Window(
        "Squiddy",
        layout(right_click_url),
        icon=ctx.icon(),
        finalize=True,
    )