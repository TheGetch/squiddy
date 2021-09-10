$cwe_file = "./cwec_v4.5.xml"

[xml]$xml = Get-Content -Path $cwe_file

$xml.Weakness_Catalog.Weaknesses.Weakness | ForEach-Object {
    $description = $_.Extended_Description
    if ($null -ne $description.p) {
        $d = "$($description.p)`n"
        $description.ul.li | Foreach-Object {
            $d += "$($_)`n"
        }

        $description = $d
    }

    $remediation = $_.Potential_Mitigations.Mitigation
    if ($remediation -is [array]) {
        $r = ""
        $remediation | ForEach-Object {
            $r += "$($_.Phase) - $($_.Description)`n`n"
        }

        $remediation = $r
    }

    $impact = $_.Common_Consequences.Consequence
    if ($impact -is [array]) {
        $i = ""
        $impact | Foreach-Object {
            $i += "$($_.Note)`n`n"
        }

        $impact = $i
    } else {
        $impact = $impact.Note
    }

    $json = @{
        "cwe" = $_.ID
        "title" = $_.Name
        "description" = $description
        "rating_impact" = $impact
        "rating_likelihood" = ""
        "impact" = $impact
        "likelihood" = $likelihood
        "remediation" = $remediation
    }

    $title = ($_.Name).Split([IO.Path]::GetInvalidFileNameChars()) -join '_'
    $json_file = "$($_.ID) - $($title).json"

    $data = $json | ConvertTo-Json
    $Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False
    [System.IO.File]::WriteAllLines("$($pwd)/export/$($json_file)", $data, $Utf8NoBomEncoding)
}
