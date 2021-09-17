import os

import PySimpleGUI as sg


def default_links():
    pass


def link(item, index):
    title = item["title"] if "title" in item else ""
    url = item["url"] if "url" in item else ""
    return [
        sg.Text(str(index + 1) + ") "),
        sg.Text(
            title,
            expand_x=True,
            enable_events=True,
            key="info_" + title,
            metadata=url,
            tooltip=url,
            font="Consolas 11 underline",
        ),
    ]


def get_links(info):
    return [(link(item, i)) for i, item in enumerate(info["links"])]


def layout(name, info):
    return [
        [
            [sg.Text(info["title"])],
            [sg.HorizontalSeparator(pad=(5, 10))],
            [sg.Input(key="info_id_old", default_text=name, visible=False)],
            [
                get_links(info),
            ],
        ]
    ]


def window(ctx, info_name, info):
    layout_info = layout(info_name, info)
    return sg.Window(
        "PenTest - Vulnerability Additional Info",
        layout_info,
        icon=ctx.icon(),
        finalize=True,
    )
