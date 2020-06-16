path = "C:\vbs"
FTPUser = "Administrator"
FTPPass = "Shanghai2020"
FTPHost = "15.83.248.196"
FTPDir = "/Scripts"

On Error Resume Next
Const copyType = 16

Set oShell = CreateObject("Shell.Application")
Set objFSO = CreateObject("Scripting.FileSystemObject")

'FTP Wait Time in ms
waitTime = 3000

strFTP = "ftp://" & FTPUser & ":" & FTPPass & "@" & FTPHost & FTPDir
Set objFTP = oShell.NameSpace(strFTP)

'Download all files under remote Scripts folder to local vbs folder.
If Not objFSO.FolderExists(path) Then
	objFSO.CreateFolder(path)
End If
If objFSO.FolderExists(path) Then
	If objFSO.FileExists(path&"\socket_server.exe") Then
		objFSO.DeleteFile(path&"\socket_server.exe")
	End If
    Set objFolder = oShell.NameSpace(path)
    objFolder.CopyHere objFTP.Items, 16
End If
If Err.Number <> 0 Then
    Wscript.Echo "Error: " & Err.Description &  " - " & Err.Number
End If
'Wait for download
Wscript.Sleep waitTime


On Error Resume Next
Dim objws
Set objws = WScript.CreateObject("wscript.shell")
objws.Run """C:\vbs\socket_server.exe""",,True