format PE GUI 4.0 DLL
entry DllEntryPoint
include 'win32a.inc'

section '.bss' readable writeable
        hLibOrg         dd ?

section '.data' data readable writeable
        force_filename  db 'C:\Program Files (x86)\Plaxis8x\force.txt',0
        szDllOrg        db 'PLXREQX.dll',0
                        dd 0xFFFFFFFF
                        dd 50
        filename        db 'C:\Program Files (x86)\Plaxis8x\Examples\BHLog.plx',0

section '.text' code readable executable
proc DllEntryPoint hinstDLL, fdwReason, lpvReserved
        mov     eax,[fdwReason]
        cmp     eax,DLL_PROCESS_ATTACH
        je      _dll_attach
        jmp     _dll_exit

_dll_attach:
        push    szDllOrg
        call    [GetModuleHandleA]
        mov     [hLibOrg],eax
        mov     eax,1

_dll_exit:
        ret
        call    ExecuteGeoSaveDlg
endp

proc ExecuteGeoSaveDlg_mod, string_list
     invoke DeleteFile, force_filename;0 on failure
     test al,al
     jne next_level

     invoke ExecuteGeoSaveDlg, [string_list]
     ret

next_level:
     mov eax, [string_list]
     mov edx,[eax]
     call dword [edx+40h] ;init array

     ;allocation
     mov edx,1
     mov eax,[string_list]
     mov ebx,eax
     mov ecx,[eax]
     call dword [ecx+30h]

     xor ecx,ecx
     mov eax,[string_list]
     mov edx,filename
     mov ebx,[eax]
     call dword [ebx+38h] ;add to array

     mov eax, 1
     ret
endp

section '.idata' import data readable writeable
library kernel,'KERNEL32.DLL',\
        blackbox, 'PLXREQX.dll'
import  kernel,\
        GetModuleHandleA, 'GetModuleHandleA',\
        DeleteFile, 'DeleteFileA'
import blackbox,\
       ExecuteGeoSaveDlg, 'ExecuteGeoSaveDlg'

section '.edata' export data readable
export  'PLXREQX.dll',\
        ExecuteOutput3DOpenDlg, 'ExecuteOutput3DOpenDlg',\
        ExecuteGeo3DSaveDlg, 'ExecuteGeo3DSaveDlg',\
        ExecuteTNLOpenDlg, 'ExecuteTNLOpenDlg',\
        ExecuteCurve3DImportDlg, 'ExecuteCurve3DImportDlg',\
        ExecuteCurveImportDlg, 'ExecuteCurveImportDlg',\
        ExecuteBatch3DTOpenDlg, 'ExecuteBatch3DTOpenDlg',\
        ExecuteBatchOpenDlg, 'ExecuteBatchOpenDlg',\
        ExecuteBatch3DTAddDlg, 'ExecuteBatch3DTAddDlg',\
        ExecuteBatchAddDlg,'ExecuteBatchAddDlg',\
        ExecuteCurve3DOpenDlg, 'ExecuteCurve3DOpenDlg',\
        ExecuteCurveOpenDlg, 'ExecuteCurveOpenDlg',\
        ExecuteOutputOpenDlg, 'ExecuteOutputOpenDlg',\
        ExecuteGeoOpenDlg, 'ExecuteGeoOpenDlg',\
        ExecuteGeoSaveDlg_mod, 'ExecuteGeoSaveDlg'
        
; The functions that we want to format should be here
ExecuteOutput3DOpenDlg db 'PLXREQX.ExecuteOutput3DOpenDlg',0
ExecuteGeo3DSaveDlg db 'PLXREQX.ExecuteGeo3DSaveDlg', 0
ExecuteGeo3DOpenDlg db 'PLXREQX.ExecuteGeo3DOpenDlg', 0
ExecuteTNLOpenDlg db 'PLXREQX.ExecuteTNLOpenDlg', 0
ExecuteCurve3DImportDlg db 'PLXREQX.ExecuteCurve3DImportDlg', 0
ExecuteCurveImportDlg db 'PLXREQX.ExecuteCurveImportDlg', 0
ExecuteBatch3DTOpenDlg db 'PLXREQX.ExecuteBatch3DTOpenDlg', 0
ExecuteBatchOpenDlg db 'PLXREQX.ExecuteBatchOpenDlg', 0
ExecuteBatch3DTAddDlg db 'PLXREQX.ExecuteBatch3DTAddDlg', 0
ExecuteBatchAddDlg db 'PLXREQX.ExecuteBatchAddDlg', 0
ExecuteCurve3DOpenDlg db 'PLXREQX.ExecuteCurve3DOpenDlg', 0
ExecuteCurveOpenDlg db 'PLXREQX.ExecuteCurveOpenDlg', 0
ExecuteOutputOpenDlg db 'PLXREQX.ExecuteOutputOpenDlg', 0
ExecuteGeoOpenDlg db 'PLXREQX.ExecuteGeoOpenDlg',0

section '.reloc' fixups data discardable