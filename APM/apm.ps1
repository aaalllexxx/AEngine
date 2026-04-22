python "$env:APPDATA\apm\apm.py" $args

$tmpFile = "$env:TEMP\apm_goto.tmp"

if (Test-Path $tmpFile) {
    # Читаем файл в кодировке OEM (866), так как goto.py сохраняет его именно в ней ради cmd.exe
    $apmGotoPath = [System.IO.File]::ReadAllText($tmpFile, [System.Text.Encoding]::GetEncoding([System.Globalization.CultureInfo]::CurrentCulture.TextInfo.OEMCodePage)).Trim()
    
    Remove-Item $tmpFile
    Set-Location -Path $apmGotoPath
}
