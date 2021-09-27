import json
import os

from urllib.parse import quote_plus

import PySimpleGUI as sg
import webbrowser

import calculate_rating
import info_layout
import vuln_layout
import attachment_layout

prediction_list, input_text, sel_item = [], "", 0


def state(ctx, event):
    """
    State monitors the GUI events for state changing actions.
    Such as changing a vulnerability title or description.
    This enables the save prompt to only happen when needed.
    """
    if (
        event
        not in (
            "About...",
            "-BOX-CWE",
            "-BOX-TITLE",
            "__TIMEOUT__",
            "attachment_list",
            "vuln_list",
        )
        and not event.startswith("expand_")
        and not event.startswith("hide_")
        and not event.startswith("info_")
        and not event.__contains__("::")
    ):
        print("marking as unsaved")
        ctx.saved = False


# Remove attachment
def rem_attachment(ctx, values):
    """
    Remove attachment from the project
    """
    if not values["attachment_list"]:
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
        ctx.set_win_prop_list("main", "attachment_list", ctx.attachment_list())


# Get Vuln info links popup
def vuln_info(ctx, window, values):
    """
    This is the '?' button on the vulnerability window.
    When clicked, it displays a list of links assocated with a CWE
    """
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
    """
    Remove vulnerability from the project
    """
    if not values["vuln_list"]:
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
        ctx.set_win_prop_list("main", "vuln_list", ctx.vuln_list())


def new_project(ctx):
    """
    Clears out the current project
    """
    ctx.new_project()
    ctx.set_win_prop("main", "appname", ctx.app_name())
    ctx.set_win_prop("main", "appid", ctx.get_id())
    ctx.set_win_prop("main", "appurl", ctx.get_url())
    ctx.set_win_prop("main", "appenv", ctx.get_env())
    ctx.set_win_prop_list("main", "vuln_list", ctx.vuln_list())
    ctx.set_win_prop_list("main", "attachment_list", ctx.attachment_list())


def save_project(ctx, values):
    """
    Save current project
    """
    if not values["appname"]:
        sg.popup_ok("Please enter an App Name", title="Save Project", keep_on_top=True)
        return

    if not values["appid"]:
        sg.popup_ok("Please enter an App Id", title="Save Project", keep_on_top=True)
        return

    ctx.set_app(values)
    ctx.save()


def load_project(ctx, values):
    """
    Loan an existing project .json file
    """
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

        # ctx.app_name(data)
        ctx.app_name = data
        ctx.app_id = data
        ctx.app_url = data
        ctx.app_env = data

        ctx.set_win_prop("main", "appname", ctx.app_name)
        ctx.set_win_prop("main", "appid", ctx.app_id)
        ctx.set_win_prop("main", "appurl", ctx.app_url)
        ctx.set_win_prop("main", "appenv", ctx.app_env)

        ctx.set_vulns(data["vulns"] if data and "vulns" in data else {})
        ctx.set_win_prop_list("main", "vuln_list", ctx.vuln_list())

        ctx.set_attachments(
            data["attachments"] if data and "attachments" in data else {}
        )
        ctx.set_win_prop_list("main", "attachment_list", ctx.attachment_list())

        ctx.saved = True


def new_edit_vuln(ctx, event, values):
    scan_id = None
    if event.endswith("::edit_vuln"):
        if not values["vuln_list"]:
            sg.popup_ok(
                "Please select a vulnerability from the list",
                title="Edit Vulnerability",
                keep_on_top=True,
            )
            return

        scan_id = values["vuln_list"][0].split(" - ")[0]

    if event.endswith("::new_vuln"):
        scan_id = "Scan-XXXX" + str(ctx.vuln_count())

    ctx.windows[scan_id] = vuln_layout.window(ctx, event, values)

    vuln_layout.update_window(ctx, scan_id)


def save_vuln(ctx, values):
    vuln_id = values["vuln_name"]
    ctx.rem_vuln(vuln_id)

    values.pop("vuln_name", None)
    values.pop("-BOX-CWE", None)
    values.pop("-BOX-TITLE", None)

    ctx.set_vuln(vuln_id, values)
    ctx.set_win_prop_list("main", "vuln_list", ctx.vuln_list())


def expandos(window, event):
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


def hideos(window, event):
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


def explain(command):
    """
    Take the current attachment command and open it in explainshell.com
    ExplainShell is a tool that breaks down the parameters of a linux command and explains what the parameters do
    """
    if not command:
        return
    explainshell = "https://explainshell.com/explain?cmd=" + quote_plus(command)
    open_url(explainshell)


def open_url(url):
    """
    Open URL in web browser
    """
    if not url:
        return
    webbrowser.open(url)


def new_edit_attachment(ctx, event, values):
    attachment_id = None

    if event.endswith("::edit_attachment"):
        if not values["attachment_list"]:
            sg.popup_ok(
                "Please select an attachment from the list",
                title="Edit Attachment",
                keep_on_top=True,
            )
            return

        attachment_id = values["attachment_list"][0]

    if event.endswith("::new_attachment"):
        attachment_id = ""

    attachment = ctx.get_attachment(attachment_id)

    print("attachment_id", attachment_id)

    ctx.windows[attachment_id] = attachment_layout.window(
        ctx, attachment, attachment_id
    )


def update_attachment(ctx, window, values):
    attachment_layout.update_window(window, values, ctx.attachments_folder, ctx.app_url)
