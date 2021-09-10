#                                       Impact
#                       Low     |   Limited    |   Moderate    | Considerable   | High
# Almost Certain    | Moderate  | Considerable | Considerable  | High           | High
# Liklely           | Limited   | Moderate     | Considerable  | Considerable   | High
# Possible          | Limited   | Moderate     | Moderate      | Considerable   | Considerable
# Unlikely          | Limited   | Limited      | Moderate      | Moderate       | Considerable
# Remote            | Low       | Limited      | Limited       | Limited        | Moderate

likelihood_values = {
    "almost certain": 4,
    "likely": 3,
    "possible": 2,
    "unlikely": 1,
    "remote": 0,
}

impact_values = {"high": 4, "considerable": 3, "moderate": 2, "limited": 1, "low": 0}

matrix = [
    ["Low", "Limited", "Limited", "Limited", "Moderate"],  # Low
    ["Limited", "Limited", "Moderate", "Moderate", "Considerable"],  # Limited
    ["Limited", "Moderate", "Moderate", "Considerable", "Considerable"],  # Moderate
    ["Limited", "Moderate", "Considerable", "Considerable", "High"],  # Considerable
    ["Moderate", "Considerable", "Considerable", "High", "High"],  # High
]

colors = {
    "Low": "Dodger Blue",
    "Limited": "SpringGreen2",
    "Moderate": "Yellow",
    "Considerable": "Orange",
    "High": "firebrick1",
}


def calculate_rating(impact="low", likelihood="remote"):
    # Impact and Likelihood would be blank on a new vuln
    if impact == "" and likelihood == "":
        return ""

    if not impact:
        impact = "Low"

    if not likelihood:
        likelihood = "Remote"

    impact_index = impact_values[impact.lower()]
    likelihood_index = likelihood_values[likelihood.lower()]

    # return impact + ' x ' + likelihood + ' = ' + matrix[impact_index][likelihood_index]
    return (
        matrix[impact_index][likelihood_index],
        colors[matrix[impact_index][likelihood_index]],
    )
