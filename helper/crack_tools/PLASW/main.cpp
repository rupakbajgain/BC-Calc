#include <iostream>
#include <windows.h>
#include <string>
#include <algorithm>
//#include <sstream>
#include <fstream>

class process{
	public:
		static PROCESS_INFORMATION launchProcess(std::string arg){
			STARTUPINFO si;
			PROCESS_INFORMATION pi;
			ZeroMemory(&si, sizeof(si));
			si.cb = sizeof(si);
			ZeroMemory(&pi, sizeof(pi));
									
			if(!CreateProcess(
				NULL,
				arg.c_str(),
				NULL,
				NULL,
				FALSE,
				0,
				NULL,
				NULL,
				&si,
				&pi
			)){
				std::cout << "Create process failed." << GetLastError() << std::endl;
				return;
			}
			
			return pi;
		}
		
		static int getExitCode(PROCESS_INFORMATION pi){
			DWORD lpExitCode = 0;
			GetExitCodeProcess(pi.hProcess, &lpExitCode);
			return lpExitCode;
		}
				
		static bool checkIfProcessIsActive(PROCESS_INFORMATION pi){
			if(pi.hProcess==NULL){
				std::cout << "Process is closed or invalied handle." << GetLastError() << std::endl;
				return false;
			}
			DWORD lpExitCode = 0;
			if(GetExitCodeProcess(pi.hProcess, &lpExitCode)==0){
				std::cout << "Cannot return exit code" << GetLastError() << std::endl;
				return false;
			}else{
				if(lpExitCode==STILL_ACTIVE){
					return true;
				}else{
					return false;
				}
				
			}
		}
		
		static bool stopProcess(PROCESS_INFORMATION pi){
			if(pi.hProcess==NULL){
				std::cout << "Process is closed or invalied handle." << GetLastError() << std::endl;
				return false;
			}
			if(!TerminateProcess(pi.hProcess, 1)){
				std::cout << "Exit process failed" << GetLastError() << std::endl;
				return false;
			}
			if(WaitForSingleObject(pi.hProcess, INFINITE)==WAIT_FAILED){
				std::cout << "Wait for process failed" << GetLastError() << std::endl;
				return false;
			}
			if(!CloseHandle(pi.hProcess)){
				std::cout << "Cannot close process handle." << GetLastError() << std::endl;
				return false;
			}else{
				pi.hProcess = NULL;
			}
			if(!CloseHandle(pi.hThread)){
				std::cout << "Cannot close thread handle." << GetLastError() << std::endl;
				return false;
			}else{
				pi.hThread = NULL;
				return true;
			}			
		}

		static void waitForProcess(PROCESS_INFORMATION pi){
			if(pi.hProcess==NULL){
				return;
			}
			if(WaitForSingleObject(pi.hProcess, INFINITE)==WAIT_FAILED){
				return;
			}
		}
	};

class mutex{
	public:
		static HANDLE waitForMutex(){
			int hMutexHandle = CreateMutex(NULL,TRUE,"wait.pro");
			if(GetLastError()==ERROR_ALREADY_EXISTS){
				WaitForSingleObject(hMutexHandle, INFINITE);
			}
			return hMutexHandle;
		}	
		
		static void releaseMutex(HANDLE hMutexHandle){
			ReleaseMutex(hMutexHandle);
			CloseHandle(hMutexHandle);
		}

};

void two_arg_mode(std::string option){
	if(option=="--reset"){
		system("del \"C:\\Program Files (x86)\\Plaxis8x\\force.txt\"");
	}
}

bool does_file_exists(std::string filename){
	std::ifstream infile(filename.c_str());
	return infile.good();
}

int main(int argc, char** argv) {
	HANDLE h = mutex::waitForMutex();
	std::string line;
	
	if (argc==1){
		two_arg_mode("--reset");
		return 0;
	}
	std::string dir = argv[1];
	if (argc==2){
		two_arg_mode(dir);
		return 0;
	}
	std::string mode = argv[2];
	std::string	cmd = "\"C:\\Program Files (x86)\\Plaxis8x\\PlasX.exe\"";
	for(int i=1;i<argc;i++){
		std::string p(argv[i]);
		if(p.find(' ')==-1){
			cmd += " " + p;
		}else{
			cmd += " \"" + p + "\"";
		}
	}
	PROCESS_INFORMATION pi = process::launchProcess(cmd);
	process::waitForProcess(pi);
	int exit_Code = process::getExitCode(pi);
	std::string force_file = "C:\\Program Files (x86)\\Plaxis8x\\force.txt";
	// Check if patch needs to be triggred
	if (!does_file_exists(force_file)){
		return exit_Code;	
	}
	
	// Now process has completed lets get the result
	std::string filename = dir + ".LAV";
	std::ifstream infile(filename.c_str());
	if (! infile) {
        exit(exit_Code);
    }
	std::ofstream outfile(force_file.c_str(), std::ios_base::app);
	if (! outfile) {
        exit(exit_Code);
    }
	
	std::string force=" ForceXY :  0 0";
	while(std::getline(infile, line)){
		int ls = line.size();
		if(ls>12)
			if(line.substr(0,12)==" ForceXY :  "){
				force = line;
			}
	}
	outfile << force.substr(12) << std::endl;
	//-----------------------------------------------
	mutex::releaseMutex(h);
	return exit_Code;
}

