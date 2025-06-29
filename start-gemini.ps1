# start-gemini.ps1

# Configura o Node no PATH
$env:Path = "C:\Users\User\node-v22.17.0-win-x64;" + $env:Path

# Muda para o diretório do projeto Gemini (se precisar ajustar, me fala)
Set-Location "C:\Users\User\Desktop\GitHub\marketing_ai_system_v1"

# Roda o Gemini CLI
gemini
