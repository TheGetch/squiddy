import json
import os
import PySimpleGUI as sg

import calculate_rating
import info_layout
import vuln_layout

prediction_list, input_text, sel_item = [], "", 0


def state(ctx, event):
    """
    State monitors the GUI events for state changing actions.
    Such as changing a vuln title or description
    This enables the prompt to save to only happen when needed.
    """
    if (
        event
        not in (
            "-BOX-CWE",
            "-BOX-TITLE",
            "attachment_list",
            "edit_attachment",
            "edit_vuln",
            "existing_project",
            "export",
            "info",
            "save_project",
            "vuln_list",
        )
        and not event.startswith("expand_")
        and not event.startswith("hide_")
        and not event.startswith("info_")
    ):
        print("marking as unsaved")
        ctx.set_saved(False)


# Remove attachment
def rem_attachment(ctx, values):
    if len(values["attachment_list"]) < 1:
        sg.popup_ok(
            "Please select an attachment from the list",
            title="Remove Attachment",
            keep_on_top=True,
        )
        return

    attachment_id = values["attachment_list"][0]

    confirm = sg.popup(
        "Are you sure you want to remove: " + attachment_id + "?",
        title="Remove Attachment",
        keep_on_top=True,
        button_type=1,
    )
    if confirm is not None and confirm in ("Yes"):
        ctx.rem_attachment(attachment_id)
        ctx.set_prop_list("main", "attachment_list", ctx.attachment_list())


# Get Vuln info links popup
def vuln_info(ctx, window, values):
    data = window["info"].metadata
    info_name = values["vuln_name"] + "_info"

    # Data metadata not defined on element, lets try to load it from the template file
    if not data:
        cwe = values["cwe"]
        title = values["title"]
        template_name = cwe + " - " + title + ".json"
        template_path = os.path.join(ctx.templates_folder, template_name)
        if not os.path.exists(template_path):
            print("Unable to locate template file")

        if os.path.exists(template_path):
            template_file = open(template_path, "r")

            try:
                data = json.load(template_file)
            except:
                pass

    # Data still not defined or if data does exist, it does not have a "links" param defined
    if not data or not "links" in data:
        sg.popup_ok(
            "Vulnerability does not have any addtional info defined.",
            title="Vulnerability Additonal Info",
            keep_on_top=True,
        )
        return

    ctx.windows[info_name] = info_layout.window(ctx, info_name, data)


def rem_vuln(ctx, values):
    if len(values["vuln_list"]) < 1:
        sg.popup_ok(
            "Please select a vulnerability from the list",
            title="Remove Vulnerability",
            keep_on_top=True,
        )
        return

    vuln_id = values["vuln_list"][0].split(" - ")[0]

    confirm = sg.popup(
        "Are you sure you want to remove: " + vuln_id + "?",
        title="Remove Vulnerability",
        keep_on_top=True,
        button_type=1,
    )
    if confirm is not None and confirm in ("Yes"):
        ctx.rem_vuln(vuln_id)
        ctx.set_prop_list("main", "vuln_list", ctx.vuln_list())


def new_project(ctx):
    ctx.new_project()
    ctx.set_prop("main", "appname", ctx.get_name())
    ctx.set_prop("main", "appid", ctx.get_id())
    ctx.set_prop("main", "appurl", ctx.get_url())
    ctx.set_prop("main", "appenv", ctx.get_env())
    ctx.set_prop_list("main", "vuln_list", ctx.vuln_list())
    ctx.set_prop_list("main", "attachment_list", ctx.attachment_list())


def save_project(ctx, values):
    if len(values["appname"]) < 1:
        sg.popup_ok("Please enter an App Name", title="Save Project", keep_on_top=True)
        return

    if len(values["appid"]) < 1:
        sg.popup_ok("Please enter an App Id", title="Save Project", keep_on_top=True)
        return

    ctx.set_app(values)
    ctx.save()


def load_project(ctx, values):
    if not ctx.saved:
        confirm = sg.popup(
            "Save current project?",
            title="Save Project",
            keep_on_top=True,
            button_type=1,
        )
        if confirm is not None and confirm in ("Yes"):
            ctx.set_app(values)
            ctx.save()

    project_name = sg.popup_get_file(
        "Load Project",
        initial_folder=ctx.projects_folder,
        file_types=(("JSON files", "*.json"),),
    )

    if project_name:
        project_file = open(project_name, "r")
        data = json.load(project_file)

        ctx.set_name(data)
        ctx.set_id(data)
        ctx.set_url(data)
        ctx.set_env(data)

        ctx.set_prop("main", "appname", ctx.get_name())
        ctx.set_prop("main", "appid", ctx.get_id())
        ctx.set_prop("main", "appurl", ctx.get_url())
        ctx.set_prop("main", "appenv", ctx.get_env())

        ctx.set_vulns(data["vulns"] if data and "vulns" in data else {})
        ctx.set_prop_list("main", "vuln_list", ctx.vuln_list())

        ctx.set_attachments(
            data["attachments"] if data and "attachments" in data else {}
        )
        ctx.set_prop_list("main", "attachment_list", ctx.attachment_list())

        ctx.saved = True


def new_edit_vuln(ctx, event, values):
    scan_id = None
    if event == "edit_vuln":
        if len(values["vuln_list"]) < 1:
            sg.popup_ok(
                "Please select a vulnerability from the list",
                title="Edit Vulnerability",
                keep_on_top=True,
            )
            return

        scan_id = values["vuln_list"][0].split(" - ")[0]

    if event == "new_vuln":
        new_vuln = True
        scan_id = "Scan-XXXX" + str(ctx.vuln_count())

    ctx.windows[scan_id] = vuln_layout.window(ctx, event, values)


def save_vuln(ctx, values):
    vuln_id = values["vuln_name"]
    ctx.rem_vuln(vuln_id)

    values.pop("vuln_name", None)
    values.pop("-BOX-CWE", None)
    values.pop("-BOX-TITLE", None)

    ctx.set_vuln(vuln_id, values)
    ctx.set_prop_list("main", "vuln_list", ctx.vuln_list())


def expandos(ctx, window, event):
    text = window[event].metadata
    target = event.split("_")[1]

    if text == "↗":
        window[target].set_size((70, 20))
        window[event].Update("↙")
        window[event].metadata = "↙"
    if text == "↙":
        window[target].set_size((70, 5))
        window[event].Update("↗")
        window[event].metadata = "↗"


def hideos(ctx, window, event):
    text = window[event].metadata
    target = "col_" + event.split("_")[1]

    if text == "hide":
        window[target].Update(visible=False)
        window[event].Update("(show)")
        window[event].metadata = "show"
    if text == "show":
        window[target].Update(visible=True)
        window[event].Update("(hide)")
        window[event].metadata = "hide"


def calc_rating(ctx, window, values):
    severity, text_color = calculate_rating.calculate_rating(
        values["rating_impact"], values["rating_likelihood"]
    )
    window["severity_rating"].Update(severity, text_color=text_color)


def predictive_text(ctx, event, window, values):
    value = None
    if event == "-BOX-CWE":
        value = values["-BOX-CWE"][0]

    if event == "-BOX-TITLE":
        value = values["-BOX-TITLE"][0]

    vuln_layout.update_window_vuln(ctx, window, value)


def predictive_cwe(ctx, window, values):
    global input_text

    text = values["cwe"].lower()
    if text == input_text:
        return
    else:
        input_text = text

    prediction_list = []
    if text:
        prediction_list = [
            item for item in ctx.get_choices() if item.lower().find(text) > -1
        ]

    window["-BOX-CWE"].update(values=prediction_list)
    window["-BOX-CWE"].update(set_to_index=sel_item)

    if len(prediction_list) > 0:
        window["-BOX-CWE-CONTAINER-"].update(visible=True)
    else:
        window["-BOX-CWE-CONTAINER-"].update(visible=False)


def predictive_title(ctx, window, values):
    global input_text

    text = values["title"].lower()
    if text == input_text:
        return
    else:
        input_text = text

    prediction_list = []
    if text:
        prediction_list = [
            item for item in ctx.get_choices() if item.lower().find(text) > -1
        ]

    window["-BOX-TITLE"].update(values=prediction_list)
    window["-BOX-TITLE"].update(set_to_index=sel_item)

    if len(prediction_list) > 0:
        window["-BOX-TITLE-CONTAINER-"].update(visible=True)
    else:
        window["-BOX-TITLE-CONTAINER-"].update(visible=False)
