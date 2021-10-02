import argparse
import json
import os
import webbrowser

import PySimpleGUI as sg

import app
import main_layout

import handlers

debug = False
theme = "DarkBlue"
parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--debug",
    help="Enable debug output if console is enabled",
    default=False,
    action="store_true",
)
parser.add_argument(
    "-t", "--theme", type=str, help="Change the UI theme", default="DarkBlue"
)
parser.add_argument(
    "-ts",
    "--themes",
    help="Get list of available themes",
    action="store_true",
)
args = parser.parse_args()

if args.debug:
    debug = args.debug

if args.theme:
    if args.theme not in sg.theme_list():
        print(f"Theme names are case sensitive. Get a list of themes using --themes")
    theme = args.theme if args.theme in sg.theme_list() else "DarkBlue"

if args.themes:
    print("Available Themes:")
    for name in sg.theme_list():
        print(name)

sg.theme(theme)
sg.set_options(font=("Consolas", 11))

ctx = app.app()

sg.SetOptions(icon=ctx.icon())


ctx.windows["main"] = main_layout.window(ctx)
ctx.windows["main"]["vuln_list"].bind("<Double-Button-1>", "::edit_vuln")
ctx.windows["main"]["attachment_list"].bind("<Double-Button-1>", "::edit_attachment")

ctx.windows["main"].perform_long_operation(
    lambda: ctx.load_templates(), "-TEMPLATES-LOADED-"
)

while True:  # Event Loop
    window, event, values = sg.read_all_windows(timeout=100)
    if debug:
        if not window:
            continue
        print(window, event, values)

    # Exit
    if event in (sg.WIN_CLOSED, "Exit") or event.endswith("::exit"):
        window.close()
        if window == ctx.main():
            break
        if "vuln_name" in values:
            ctx.windows[values["vuln_name"]] = None
        continue

    # Handle events to control saved state
    handlers.state(ctx, event)

    if event in ("-TEMPLATES-LOADED-"):
        print(len(ctx.templates))

    # Main Window - About Menu
    if event in ("About..."):
        url = "https://github.com/jayrox/squiddy"
        handlers.open_url(url)

    # Main Window - App Name
    if event in ("appname"):
        ctx.app_name = values["appname"]

    # Main Window - App Id
    if event in ("appid"):
        ctx.app_id = values["appid"]

    # Main Window - App URL
    if event in ("appurl"):
        ctx.app_url = values["appurl"]

    # Main Window - App Env
    if event in ("appenv"):
        ctx.app_env = values["appenv"]

    # Load Project
    if event.endswith("::existing_project"):
        handlers.load_project(ctx, values)

    # New Project
    if event.endswith("::new_project"):
        handlers.new_project(ctx)

    # Save Project
    if event.endswith("::save_project"):
        handlers.save_project(ctx, values)

    # Main Window - Name - Right click - Copy
    if event.endswith("::copy_name"):
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(ctx.app_name)

    # Main Window - ID - Right click - Copy
    if event.endswith("::copy_id"):
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(ctx.app_id)

    # Main Window - URL - Right click - Copy
    if event.endswith("::copy_url"):
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(ctx.app_url)

    # Main Window - Env - Right click - Copy
    if event.endswith("::copy_env"):
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(ctx.app_env)

    # Main Window - URL - Right click - Open Url
    if event.endswith("::open_url"):
        handlers.open_url(values["appurl"])

    # New or Edit Vuln
    if event.endswith("::edit_vuln") or event.endswith("::new_vuln"):
        handlers.new_edit_vuln(ctx, event, values)

    # Save Vuln
    if event.endswith("::save_vuln"):
        handlers.save_vuln(ctx, window, values)

    # Remove Vuln
    if event.endswith("::rem_vuln"):
        handlers.rem_vuln(ctx, values)

    # Vuln Expandos
    if event.startswith("expand_"):
        handlers.expandos(window, event)

    # Vuln Hide/Show
    if event.startswith("hide_"):
        handlers.hideos(window, event)

    # Vuln Impact and Likelihood calculation and coloring
    if event.startswith("rating_"):
        handlers.calc_rating(ctx, window, values)

    # Export Vuln
    if event.endswith("::export"):
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

    # Vuln Info
    if event.endswith("::info"):
        handlers.vuln_info(ctx, window, values)

    # Additional Vuln Info link has been clicked
    if event.startswith("info_"):
        webbrowser.open(window[event].metadata)

    # Remove attachment
    if event.endswith("::rem_attachment"):
        handlers.rem_attachment(ctx, values)

    # Add Attachment
    if event.endswith("::edit_attachment") or event.endswith("::new_attachment"):
        handlers.new_edit_attachment(ctx, event, values)

    # Attachment type drop down
    if event in ("attachment_type"):
        handlers.update_attachment(ctx, window, values)

    # Save attachment
    if event.endswith("::save_attachment"):
        if not values["attachment_id"]:
            sg.popup_ok(
                "Please enter a name",
                title="Save Attachment",
                keep_on_top=True,
            )
            continue

        attachment_id = values["attachment_id_old"]
        ctx.attachments.pop(attachment_id, None)

        values.pop("attachment_id_old", None)
        ctx.attachments[values["attachment_id"]] = values

        ctx.set_win_prop_list("main", "attachment_list", ctx.attachment_list())

    # ExplainShell.com command explainer
    if event.endswith("::explain"):
        handlers.explain(values["command"])

    # Right click menu - Select All
    if event == "Select All":
        window["results"].Widget.selection_clear()
        window["results"].Widget.tag_add("sel", "1.0", "end")

    # Right click menu - Copy
    if event == "Copy":
        try:
            text = window["results"].Widget.selection_get()
            window.TKroot.clipboard_clear()
            window.TKroot.clipboard_append(text)
        except:
            print("Nothing selected")

    # Right click menu - Paste
    if event == "Paste":
        window["results"].Widget.insert(sg.tk.INSERT, window.TKroot.clipboard_get())

    # Right click menu - Cut
    # if event == "Cut":
    #     try:
    #         text = mline.Widget.selection_get()
    #         a_win.TKroot.clipboard_clear()
    #         a_win.TKroot.clipboard_append(text)
    #         mline.update("")
    #     except:
    #         print("Nothing selected")
