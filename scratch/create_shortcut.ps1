$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $DesktopPath "Penjadwalan.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "D:\Jadwal\start_sitab.bat"
$Shortcut.WorkingDirectory = "D:\Jadwal"
$Shortcut.Description = "Luncurkan Aplikasi Penjadwalan SITAB"
# shell32.dll, 22 is a nice calendar/timetable icon on Windows
$Shortcut.IconLocation = "shell32.dll,22" 
$Shortcut.Save()

Write-Host "Shortcut Penjadwalan berhasil dibuat di Desktop!"
Write-Host "Lokasi: $ShortcutPath"
