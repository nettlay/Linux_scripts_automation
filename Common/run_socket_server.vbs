path = "C:\vbs"
FTPUser = "Administrator"
FTPPass = "Shanghai2020"
FTPHost = "15.83.248.196"
FTPDir = "/Scripts"
LogPath = "C:\vbs\vbs_log.txt"

Const copyType = 16

Dim download
Call KillProcess("socket_server.exe")
download = DownloadEXE()
If download = True Then 
	Call WriteLog(LogPath, "Download exe file successful.")
	Call RunEXE()
Else
	Call WriteLog(LogPath, "Fail to Download exe file first time, download again.")
	Call DownloadEXE()
	Call RunEXE()
End If

'Download all files under remote Scripts folder to local vbs folder.
Function DownloadEXE()

	On Error Resume Next
	Dim objFSO, oShell, strFTP, objFTP, objLocal, count, i
	Set objFSO = CreateObject("Scripting.FileSystemObject")	
	If Not objFSO.FolderExists(path) Then
		Call WriteLog(LogPath, path & " doesn't exist, create it.")
		objFSO.CreateFolder(path)
	ElseIf objFSO.FileExists(path&"\socket_server.exe") Then
		Call WriteLog(LogPath, path & "\socket_server.exe have already exist, delete it.")
		objFSO.DeleteFile(path&"\socket_server.exe")
		WScript.Sleep 2000
	End If
	
	Set oShell = CreateObject("Shell.Application")
	strFTP = "ftp://" & FTPUser & ":" & FTPPass & "@" & FTPHost & FTPDir
	Call WriteLog(LogPath, "Start to connect FTP " & strFTP)
	Set objFTP = oShell.NameSpace(strFTP)
	Set objLocal = oShell.NameSpace(path)
	    objLocal.CopyHere objFTP.Items, 16 
	count = 0 
	For i = 1 To 5
		WScript.Sleep 3000
		count = count + 1
		If objFSO.FileExists(path&"\socket_server.exe") Then
			DownloadEXE = True
			Call WriteLog(LogPath, "Download successful.")
			Exit For
		End If
	Next
	If count > 5 Then
		DownloadEXE = False
		Call WriteLog(LogPath, "Download fail after timeout.")
	End If 
		
	Set objFSO = Nothing
	Set objFTP = Nothing
	Set objLocal = Nothing
	Set oShell = Nothing
	Call CaptureErr()	
End Function

'Execute exe file.
Sub RunEXE()
	On Error Resume Next
	Dim objws
	Set objws = WScript.CreateObject("wscript.shell")
	'objws.Run """C:\vbs\socket_server.exe""",,True
	objws.Run "cmd /c c:\vbs\socket_server.exe", vbhide
	Set objws = Nothing
	WScript.Sleep 3000
	If QueryProcess("socket_server.exe") = True Then
		Call WriteLog(LogPath, "Run exe file successfully.")
	Else
		Call WriteLog(LogPath, "Run exe file fail, no process detected.")
	End If
	Call CaptureErr()
End Sub

'Kill process if it exists
Sub KillProcess(processName)
	On Error Resume Next
	Dim strComputer, wmi, processes, process
	strComputer = "."
	Set wmi = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
	Set processes = wmi.ExecQuery("select * from win32_process where name='" & processName & "'")
	for each process in processes
		process.terminate()
	next
	wscript.sleep 5000
	Set processes = Nothing
	Set wmi = Nothing
	Call CaptureErr()
End Sub

'Query the process exists or not
Function QueryProcess(processName)
	On Error Resume Next
	Dim strComputer, wmi, processes, process, flag
	flag = False
	strComputer = "."
	Set wmi = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
	Set processes = wmi.ExecQuery("select * from win32_process")
	for each process in processes
		If process.Name = processName Then
			flag = True
			Exit For
		End If		
	next
	Set processes = Nothing
	Set wmi = Nothing
	QueryProcess = flag
	Call CaptureErr()
End Function

'Write error into log file.
Sub CaptureErr()
	If Err.Number <> 0 Then
		Call WriteLog(LogPath, "Error: " & Err.Description &  " - " & Err.Number)
	End If
End Sub

'Log
Function WriteLog(sFileName, sText)
'	On Error Resume Next
    Dim fs, fso, sLog
    sLog = Now() & ": " & sText
 
    set fs = CreateObject("Scripting.FileSystemObject")
    set fso = fs.OpenTextFile(sFileName, 8, True)  'True means if file doesn't exist, create one.
    fso.WriteLine sLog
    fso.Close
    set fso = Nothing
    set fs = Nothing
End Function