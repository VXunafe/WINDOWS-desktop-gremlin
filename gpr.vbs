Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "scripts\run-gp.bat" & Chr(34), 0
Set WshShell = Nothing