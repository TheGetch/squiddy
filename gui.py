import json
import os
import webbrowser

import PySimpleGUI as sg

import app
import calculate_rating
import attachment_layout
import vuln_layout

import handlers

debug = False

sg.theme("DarkBlue")
sg.set_options(font=("Consolas", 11))

ctx = app.app()

sg.SetOptions(icon=ctx.icon())


def expando(key):
    return sg.Submit("↗", key=key, tooltip="Expand")


# Main window
layout_main = [
    [
        sg.Submit("New Project", key="new_project"),
        sg.Submit("Save Project", key="save_project"),
        sg.Submit("Load Project", key="existing_project"),
    ],
    [sg.Text("Name", size=(15, 1)), sg.Input(key="appname", enable_events=True)],
    [sg.Text("ID", size=(15, 1)), sg.Input(key="appid", enable_events=True)],
    [sg.Text("URL", size=(15, 1)), sg.Input(key="appurl", enable_events=True)],
    [sg.Text("Environment", size=(15, 1)), sg.Input(key="appenv", enable_events=True)],
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
        [
            sg.Submit("New", key="new_vuln"),
            sg.Submit("Edit", key="edit_vuln"),
            sg.Submit("Remove", key="rem_vuln"),
        ],
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
        [
            sg.Submit("New", key="new_attachment"),
            sg.Submit("Edit", key="edit_attachment"),
            sg.Submit("Remove", key="rem_attachment"),
        ],
    ],
]

ctx.windows["main"] = sg.Window("Squiddy", layout_main, icon=ctx.icon(), finalize=True)

while True:  # Event Loop
    window, event, values = sg.read_all_windows()
    if debug:
        print(window, event, values)

    # Exit
    if event in (sg.WIN_CLOSED, "Exit"):
        window.close()
        if window == ctx.main():
            break

        if "vuln_name" in values:
            ctx.windows[values["vuln_name"]] = None

        continue

    # Handle events to control saved state
    handlers.state(ctx, event)

    # Load Project
    if event in ("existing_project"):
        handlers.load_project(ctx, values)

    # New Project
    if event in ("new_project"):
        handlers.new_project(ctx)

    # Save Project
    if event in ("save_project"):
        handlers.save_project(ctx, values)

    # New or Edit Vuln
    if event in ("edit_vuln", "new_vuln"):
        handlers.new_edit_vuln(ctx, event, values)

    # Save Vuln
    if event in ("save_vuln"):
        handlers.save_vuln(ctx, values)

    # Vuln Expandos
    if event.startswith("expand_"):
        handlers.expandos(ctx, window, event)

    # Vuln Hide/Show
    if event.startswith("hide_"):
        handlers.hideos(ctx, window, event)

    # Vuln Impact and Likelihood calculation and coloring
    if event.startswith("rating_"):
        handlers.calc_rating(ctx, window, values)

    # Export Vuln
    if event in ("export"):
        ctx.save_template(window, values)

    # Vuln Predictive Text
    if event in ("-BOX-CWE", "-BOX-TITLE"):
        handlers.predictive_text(ctx, event, window, values)

    # Title predictive text stuff
    if event == "title":
        handlers.predictive_title(ctx, window, values)

    # CWE predictive text stuff
    if event == "cwe":
        handlers.predictive_cwe(ctx, window, values)

    # Remove Vuln
    if event in ("rem_vuln"):
        handlers.rem_vuln(ctx, values)

    # Remove attachment
    if event in ("rem_attachment"):
        handlers.rem_attachment(ctx, values)

    # Vuln Info
    if event in ("info"):
        handlers.vuln_info(ctx, window, values)

    # Additional Vuln Info link has been clicked
    if event.startswith("info_"):
        webbrowser.open(window[event].metadata)

    # Add Attachment
    if event in ("edit_attachment", "new_attachment"):
        attachment_id = None
        new_attachment = False

        if event == "edit_attachment":

            if len(values["attachment_list"]) < 1:
                sg.popup_ok(
                    "Please select an attachment from the list",
                    title="Edit Attachment",
                    keep_on_top=True,
                )
                continue

            attachment_id = values["attachment_list"][0]

        if event == "new_attachment":
            new_attachment = True
            attachment_id = ""

        attachment = ctx.get_attachment(attachment_id)

        a_layout = attachment_layout.layout(
            ctx, attachment, attachment_id, values["appurl"]
        )
        a_win = sg.Window("PenTest - Attachment", a_layout, icon=ctx.icon())

        mline: sg.Multiline = a_win["results"]

        while True:  # Event Loop
            event_attachment, values_attachment = a_win.read()
            print(event_attachment, values_attachment)

            if event_attachment in (sg.WIN_CLOSED, "Exit", "Cancel"):
                a_win.close()
                break

            if event_attachment in ("attachment_type"):
                attachment_layout.update_window(
                    a_win, values_attachment, ctx.attachments_folder, values["appurl"]
                )

            if event_attachment in ("expand_results"):
                text = a_win[event_attachment].get_text()
                target = event_attachment.split("_")[1]

                if text == "↗":
                    a_win[target].set_size((70, 20))
                    a_win[event_attachment].Update("↙")
                if text == "↙":
                    a_win[target].set_size((70, 5))
                    a_win[event_attachment].Update("↗")

            if event_attachment in ("save"):
                if len(values_attachment["attachment_id"]) < 1:
                    sg.popup_ok(
                        "Please enter an name",
                        title="Save Attachment",
                        keep_on_top=True,
                    )
                    continue

                attachment_id = values_attachment["attachment_id_old"]
                ctx.attachments.pop(attachment_id, None)

                values_attachment.pop("attachment_id_old", None)
                ctx.attachments[values_attachment["attachment_id"]] = values_attachment

                ctx.set_prop_list("main", "attachment_list", ctx.attachment_list())

            if event_attachment == "Select All":
                mline.Widget.selection_clear()
                mline.Widget.tag_add("sel", "1.0", "end")
            elif event_attachment == "Copy":
                try:
                    text = mline.Widget.selection_get()
                    a_win.TKroot.clipboard_clear()
                    a_win.TKroot.clipboard_append(text)
                except:
                    print("Nothing selected")
            elif event_attachment == "Paste":
                mline.Widget.insert(sg.tk.INSERT, a_win.TKroot.clipboard_get())
            # elif event_attachment == "Cut":
            #     try:
            #         text = mline.Widget.selection_get()
            #         a_win.TKroot.clipboard_clear()
            #         a_win.TKroot.clipboard_append(text)
            #         mline.update("")
            #     except:
            #         print("Nothing selected")
