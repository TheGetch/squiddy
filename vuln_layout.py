import json
import os
import PySimpleGUI as sg

import calculate_rating


impact_options = ["High", "Considerable", "Moderate", "Limited", "Low"]
likelihood_options = ["Almost Certain", "Likely", "Possible", "Unlikely", "Remote"]
status_options = ["Open", "Closed", "Closed Pending Confirmation"]

mline_width = 67


def section(title, content):
    return [
        [
            sg.Multiline(
                content,
                key=title,
                size=(mline_width, 10),
                expand_x=True,
                expand_y=True,
            ),
        ],
    ]


def section_combo(title, content, options, default_value):
    return [
        [
            sg.Column(
                [
                    [
                        sg.Combo(
                            options,
                            default_value=default_value,
                            key="rating_" + title,
                            readonly=True,
                            enable_events=True,
                        ),
                    ]
                ],
                element_justification="right",
                vertical_alignment="bottom",
                expand_x=True,
            ),
        ],
        [
            sg.Multiline(
                content,
                key=title,
                size=(mline_width, 10),
                expand_x=True,
                expand_y=True,
            ),
        ],
    ]


menu_def = [
    [
        "&Vulnerability",
        [
            "&Save::save_vuln",
            "&Export::export",
        ],
    ],
    ["&Additional Info", ["&Links::info"]],
]


def layout(scan_id):
    input_width = 45
    num_items_to_show = 4

    return [
        [sg.Menu(menu_def, tearoff=False, pad=(200, 1))],
        [
            sg.Column(
                [
                    [sg.Input(key="vuln_name", default_text=scan_id, visible=False)],
                    [
                        sg.Text("Scan Id", size=(15, 1)),
                        sg.Input(key="scanid", default_text=scan_id),
                    ],
                    [
                        sg.Text("Title", size=(15, 1)),
                        sg.Input("", key="title", enable_events=True),
                    ],
                    [
                        sg.pin(
                            sg.Column(
                                [
                                    [
                                        sg.Listbox(
                                            values=[],
                                            size=(input_width, num_items_to_show),
                                            enable_events=True,
                                            key="-BOX-TITLE",
                                            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                                            no_scrollbar=True,
                                            pad=((139, 0), (2, 2)),
                                        )
                                    ]
                                ],
                                key="-BOX-TITLE-CONTAINER-",
                                pad=(0, 0),
                                visible=False,
                            )
                        )
                    ],
                    [
                        sg.Text("CWE", size=(15, 1)),
                        sg.Input("", key="cwe", enable_events=True),
                    ],
                    [
                        sg.pin(
                            sg.Column(
                                [
                                    [
                                        sg.Listbox(
                                            values=[],
                                            size=(input_width, num_items_to_show),
                                            enable_events=True,
                                            key="-BOX-CWE",
                                            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                                            no_scrollbar=True,
                                            pad=((139, 0), (2, 2)),
                                        )
                                    ]
                                ],
                                key="-BOX-CWE-CONTAINER-",
                                pad=(0, 0),
                                visible=False,
                            )
                        )
                    ],
                    [
                        sg.Text("Status", size=(15, 1)),
                        sg.Combo(
                            status_options,
                            default_value="",
                            key="status",
                            readonly=True,
                            enable_events=True,
                        ),
                    ],
                    [
                        sg.Text("Severity", size=(15, 1)),
                        sg.Text(
                            "",
                            key="severity_rating",
                            size=(40, 1),
                            text_color="Black",
                        ),
                        sg.Input(key="severity", visible=False),
                    ],
                ],
                element_justification="left",
            ),
            sg.Text(
                "?",
                key="info",
                size=(1, 1),
                tooltip="Links for vulnerability information",
                enable_events=True,
                visible=False,
            ),
        ],
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab(
                            "Description",
                            section("description", ""),
                        ),
                        sg.Tab(
                            "Replication",
                            section("replication", ""),
                        ),
                        sg.Tab(
                            "Impact",
                            section_combo("impact", "", impact_options, ""),
                        ),
                        sg.Tab(
                            "Likelihood",
                            section_combo(
                                "likelihood",
                                "",
                                likelihood_options,
                                "",
                            ),
                        ),
                        sg.Tab(
                            "Remediation",
                            section("remediation", ""),
                        ),
                    ]
                ],
                tab_location="centertop",
                border_width=5,
                expand_x=True,
                expand_y=True,
            )
        ],
    ]


def update_window_vuln(ctx, window, value):
    window["-BOX-CWE-CONTAINER-"].update(visible=False)
    window["-BOX-TITLE-CONTAINER-"].update(visible=False)

    value = value.replace("* ", "")
    cwe, title = value.split(" - ")

    template_path = ctx.get_template(cwe, title)
    if not os.path.exists(template_path):
        print("[Vuln] Unable to locate template file")
        return

    template_file = open(template_path, "r")

    data = None
    try:
        data = json.load(template_file)
    except:
        pass

    title = data["title"] if data and "title" in data else ""
    cwe = data["cwe"] if data and "cwe" in data else ""

    description = data["description"] if data and "description" in data else ""
    impact = data["impact"] if data and "impact" in data else ""
    likelihood = data["likelihood"] if data and "likelihood" in data else ""
    remediation = data["remediation"] if data and "remediation" in data else ""

    window["cwe"].Update(cwe)
    window["title"].Update(title)
    window["description"].update(value=description)
    window["impact"].update(value=impact)
    window["likelihood"].update(value=likelihood)
    window["remediation"].update(value=remediation)
    window["info"].metadata = data
    window["replication"].update(value="")
    window["rating_impact"].update(value="")
    window["rating_likelihood"].update(value="")
    window["severity_rating"].Update("", text_color="Black")
    window["info"].metadata = data


def update_window(ctx, scan_id):
    window = ctx.windows[scan_id]
    vuln = ctx.get_vuln(scan_id)

    # Description
    description = vuln["description"] if vuln and "description" in vuln else ""

    # Replication
    replication = vuln["replication"] if vuln and "replication" in vuln else ""

    # Impact
    impact = vuln["impact"] if vuln and "impact" in vuln else ""

    # Likelihood
    likelihood = vuln["likelihood"] if vuln and "likelihood" in vuln else ""

    # Remediation
    remediation = vuln["remediation"] if vuln and "remediation" in vuln else ""

    # CWE
    cwe = vuln["cwe"] if vuln and "cwe" in vuln else ""

    # Title
    title = vuln["title"] if vuln and "title" in vuln else ""

    # Status
    status = vuln["status"] if vuln and "status" in vuln else ""
    if status not in status_options:
        status = "Open"

    # Impact
    impact_rating = vuln["rating_impact"] if vuln and "rating_impact" in vuln else ""
    if impact_rating not in impact_options:
        impact_rating = ""

    # Likelihood
    likelihood_rating = (
        vuln["rating_likelihood"] if vuln and "rating_likelihood" in vuln else ""
    )
    if likelihood_rating not in likelihood_options:
        likelihood_rating = ""

    # Severity
    severity, text_color = None, None
    try:
        severity = calculate_rating.calculate_rating(impact_rating, likelihood_rating)
        severity, text_color = calculate_rating.calculate_rating(
            impact_rating, likelihood_rating
        )
    except:
        pass

    # Metadata for the Links button
    data = None
    if cwe and title:
        template_name = f"{cwe} - {title}.json"
        template_path = os.path.join(ctx.templates_folder, template_name)

        if os.path.exists(template_path):
            template_file = open(template_path, "r")
            try:
                data = json.load(template_file)
            except:
                pass
        else:
            print("[Vuln] Unable to locate template file:", template_path)

    window["vuln_name"].Update(scan_id)
    window["scanid"].Update(scan_id)
    window["status"].Update(status)
    window["cwe"].Update(cwe)
    window["title"].Update(title)
    window["description"].update(value=description)
    window["replication"].update(value=replication)
    window["impact"].update(value=impact)
    window["likelihood"].update(value=likelihood)
    window["remediation"].update(value=remediation)
    window["rating_impact"].update(value=impact_rating)
    window["rating_likelihood"].update(value=likelihood_rating)
    window["severity_rating"].Update(severity, text_color=text_color)
    window["severity"].update(value=severity)
    window["info"].metadata = data


def window(ctx, event, values):
    scan_id = None

    if event == "edit_vuln":
        if not values["vuln_list"]:
            sg.popup_ok(
                "Please select a vulnerability from the list",
                title="Edit Vulnerability",
                keep_on_top=True,
            )
            return

        scan_id = values["vuln_list"][0].split(" - ")[0]

    if event == "new_vuln":
        scan_id = "Scan-XXXX" + str(ctx.vuln_count())

    layout_vuln = layout(scan_id)
    return sg.Window(
        "Squiddy - Vulnerability",
        layout_vuln,
        icon=ctx.icon(),
        finalize=True,
        resizable=True,
    )
