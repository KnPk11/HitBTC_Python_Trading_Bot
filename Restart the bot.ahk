#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
#singleinstance

loop,
{
	Run, "Бот.py"
	Sleep, 1200000
	SetTitleMatchMode, 2
	WinActivate
	WinWaitActive, py.exe
	WinClose
	Sleep, 5000
}