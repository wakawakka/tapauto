@echo off
for /f "tokens=*" %%a in (url_list.txt) do (
  echo line=%%a
  C:\Users\aburgerfuck\AppData\Local\MEGAcmd\MEGAclient.exe get %%a
)