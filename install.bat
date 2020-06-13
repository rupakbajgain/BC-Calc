echo off
cls
echo ----------- Installing requirements ---------------
pip install -r requirements.txt

echo --------------- Installing patch ------------------
if exist "C:\Program Files (x86)\Plaxis8x\plasx.exe" (
echo --------------- Old Patch Found -------------------
del "C:\Program Files (x86)\Plaxis8x\plasw.exe"
del "C:\Program Files (x86)\Plaxis8x\plxreq.dll"

copy ".\helper\crack_tools\plasw\plasw.exe" "C:\Program Files (x86)\Plaxis8x\"
copy ".\helper\crack_tools\plxreq\plxreq.dll" "C:\Program Files (x86)\Plaxis8x\"

) else (
echo ---------------- Adding new patch -----------------
ren "C:\Program Files (x86)\Plaxis8x\plasw.exe" "plasx.exe"
ren "C:\Program Files (x86)\Plaxis8x\plxreq.dll" "plxreqx.dll"

copy ".\helper\crack_tools\plasw\plasw.exe" "C:\Program Files (x86)\Plaxis8x\"
copy ".\helper\crack_tools\plxreq\plxreq.dll" "C:\Program Files (x86)\Plaxis8x\"
)
pause