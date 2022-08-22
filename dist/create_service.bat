pushd %~dp0
    nssm.exe install "SERVER_TXT_TO_OPC" "main.exe"
    nssm.exe set "SERVER_TXT_TO_OPC" AppDirectory %~dp0
    nssm.exe set "Converter_TXT_TO_OPC_service" Start SERVICE_AUTO_START