; Gera um instalador de verdade a partir do binário já produzido pelo PyInstaller

#define MyAppName "Sticker Notes"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Seu Nome"
#define MyAppExeName "sticker-notes.exe"

[Setup]
AppId={{14BD8E46-1D10-4693-9546-8DC2FD3DCE59}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\..\dist
OutputBaseFilename=Sticker-Notes-Setup
SetupIconFile=..\icons\sticker-notes.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupicon"; Description: "Iniciar o Sticker Notes automaticamente com o Windows"; GroupDescription: "Opções de inicialização:"

[Files]
Source: "..\..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Registry]
; Remove a chave de registro Run legada (criada por versões antigas do app)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: none; ValueName: "StickerNotes"; Flags: deletevalue uninsdeletevalue

[Run]
; Se o usuário marcou a opção de startup, remove a Tarefa Agendada antes de criar o atalho
Filename: "{cmd}"; Parameters: "/C schtasks /Delete /TN StickerNotes /F"; \
  Flags: runhidden nowait; Tasks: startupicon; RunOnceId: "RemoverTarefaAoInstalar"
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir o {#MyAppName} agora"; \
  Flags: nowait postinstall skipifsilent

[UninstallRun]
; Ao desinstalar: remove Tarefa Agendada e chave de registro (se existirem)
Filename: "{cmd}"; Parameters: "/C schtasks /Delete /TN StickerNotes /F"; \
  Flags: runhidden; RunOnceId: "RemoverTarefaAgendada"
