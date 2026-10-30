## Windows and PowerShell

- Use PowerShell tools (`Get-ChildItem`, `Select-String`) when `rg` is unavailable.
- In a nested `powershell.exe -Command "..."` escape `$` with a backtick or use a script block; do not put `cmd` between PowerShell and its command.
- Keep the repository on the Windows file system; moving it into WSL needs an explicit decision.
- Preserve each file's existing encoding and line endings.
