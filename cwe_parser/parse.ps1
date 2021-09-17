$cwe_file = "./cwec_v4.5.xml"

[xml]$xml = Get-Content -Path $cwe_file

$xml.Weakness_Catalog.Weaknesses.Weakness | ForEach-Object {
    $description = $_.Extended_Description
    if ($null -ne $description.p) {
        $d = "$($description.p)`n"
        $description.ul.li | ForEach-Object {
            $d += "$($_)`n"
        }

        $description = $d
    }

    if (-not ([string]::IsNullOrEmpty($description))) {
        $description = $description.Trim()
    }
    else {
        $description = ""
    }

    $mitigations = @()
    $_.Potential_Mitigations.Mitigation | Select-Object -Property Phase, Description | ForEach-Object {
        $mitigation = ""
        if (-not ([string]::IsNullOrEmpty($_.Phase))) {
            $mitigation += $_.Phase + ":`n"
        }

        if (($_.Description).GetType() -eq [System.Xml.XmlElement]) {
            $mitigation += [string]::Join("`n", $_.Description.InnerText)
        }
        else {
            $mitigation += ($_.Description).Trim()
        }

        $mitigations += $mitigation
    }

    $remdiation = $mitigation -join "`n`n"

    $impact = $_.Common_Consequences.Consequence
    if ($impact -is [array]) {
        $i = ""
        $impact | ForEach-Object {
            $i += "$($_.Note)`n`n"
        }
        $impact = $i
    }
    else {
        $impact = $impact.Note
    }

    if (-not ([string]::IsNullOrEmpty($impact))) {
        $impact = $impact.Trim()
    }
    else {
        $impact = ""
    }

    $json = [ordered]@{
        "title"             = $_.Name
        "cwe"               = $_.ID
        "description"       = $description
        "impact"            = $impact
        "rating_impact"     = ""
        "likelihood"        = ""
        "rating_likelihood" = ""
        "remediation"       = $remdiation
        "links"             = @(
            [ordered]@{
                "title" = "CWE-$($_.ID) | CWE MITRE"
                "url"   = "https://cwe.mitre.org/data/definitions/$($_.ID).html"
            },
            [ordered]@{
                "title" = "CWE-$($_.ID) | Security Database"
                "url"   = "https://www.security-database.com/cwe.php?name=CWE-$($_.ID)"
            },
            [ordered]@{
                "title" = "CWE-$($_.ID) | CVE Details"
                "url"   = "https://www.cvedetails.com/cwe-details/$($_.ID)/"
            },
            [ordered]@{
                "title" = "CWE-$($_.ID) | CVE Details - Vulnerabilities"
                "url"   = "https://www.cvedetails.com/vulnerability-list/cweid-$($_.ID)/vulnerabilities.html"
            },
            [ordered]@{
                "title" = "CWE-$($_.ID) | CIRCL"
                "url"   = "https://cve.circl.lu/cwe/$($_.ID)"
            }
        )
    }

    $title = ($_.Name).Split([IO.Path]::GetInvalidFileNameChars()) -join '_'
    $json_file = "$($_.ID) - $($title).json"

    $data = $json | ConvertTo-Json
    $Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False
    [System.IO.File]::WriteAllLines("$($pwd)/export/$($json_file)", $data, $Utf8NoBomEncoding)
}

# $14 = $xml.Weakness_Catalog.Weaknesses.Weakness | Where-Object { $_.ID -eq "8" }

# "Description"
# $14.Extended_Description | ForEach-Object {
#     $_.p
#     $_.ul.li | ForEach-Object {
#         $_
#     }

# }

# "Impact"
# $14.Common_Consequences.Consequence | ForEach-Object {
#     $_.Note
# }

# "Mitigation"
# $remdiation = $14.Potential_Mitigations.Mitigation
# if ($remdiation -is [array]) {
#     Write-Host "Is Array"
#     $r = ""
#     $remdiation | ForEach-Object {
#         $phase = $_.Phase
#         $mit_description = ""
#         ($_.Description).GetType()
#         if (($_.Description).GetType() -eq [System.Xml.XmlElement]) {
#             Write-Host "XmlElement" - -ForegroundColor Gree
#             $_.Description | ForEach-Object {
#                 $mit_description += "$($_.InnerText)`n"
#             }
#         }
#         else {
#             Write-Host "Else" -ForegroundColor Red
#             $mit_description = $_.Description
#         }
#         $r += "$($phase) - $($mit_description)`n`n"
#     }
#     $remdiation = $r
# }
# else {
#     Write-Host "Not Array"
#     $remdiation = "$($remdiation.Phase) - $($remdiation.Description)`n`n"
# }

# $remdiation

# $14.Potential_Mitigations.Mitigation

# [string]::Join("`n", $14.Potential_Mitigations.Mitigation )

# [string]::Join("`n", ($14.Potential_Mitigations.Mitigation | Select-Object -Property Phase, Description))

# $mitigation = @()
# $14.Potential_Mitigations.Mitigation | Select-Object -Property Phase, Description | ForEach-Object {
#     # Write-Host "Phase:" $_.Phase
#     # Write-Host "Description: " $_.Description
#     # Write-Host "Type: " ($_.Description).GetType()

#     if (($_.Description).GetType() -eq [System.Xml.XmlElement]) {
#         $mitigation += ($_.Phase + ":`n" + [string]::Join("`n", $_.Description.InnerText))
#     }
#     else {
#         $mitigation += ($_.Phase + ":`n" + $_.Description)
#     }
# }

# $mitigation -join "`n`n"
