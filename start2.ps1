#!/usr/bin/env pwsh
[Console]::TreatControlCAsInput = $True
# [System.Environment]::OSVersion.Platform

$host.UI.RawUI.ForegroundColor = "Yellow"
echo "Starting Editor"
$job1 = Start-Job -Name LitteBotEditor -ScriptBlock {
  cd D:\PLASTICSCM_LITTLEBOT\LITTE_BOT\LitteBotEditor;
   python3 ./LitteBotEditor.py
}

$host.UI.RawUI.ForegroundColor = "Magenta"
echo "Starting Sound"
$job4 = Start-Job -Name LitteBotSound -ScriptBlock {
  cd D:\PLASTICSCM_LITTLEBOT\LITTE_BOT\LitteBotServer;
   python3 ./LitteBotSound.py
}

$host.UI.RawUI.ForegroundColor = "White"
echo "Starting Brain"
$job2 = Start-Job -Name LitteBotBrain -ScriptBlock {
  cd D:\PLASTICSCM_LITTLEBOT\LITTE_BOT\LitteBotServer;
   python3 ./LitteBotBrain.py
}

$host.UI.RawUI.ForegroundColor = "Cyan"
echo "Starting Server"
$job3 = Start-Job -Name LitteBotServer -ScriptBlock {
  cd D:\PLASTICSCM_LITTLEBOT\LITTE_BOT\LitteBotServer
  Start-Sleep -Seconds 25;
    python3 ./LitteBotServer.py
}

While (Get-Job -State "Running")
{
  $host.UI.RawUI.ForegroundColor = "Yellow"
  Receive-Job -Name LitteBotEditor
  $host.UI.RawUI.ForegroundColor = "Magenta"
  Receive-Job -Name LitteBotSound
  $host.UI.RawUI.ForegroundColor = "White"
  Receive-Job -Name LitteBotBrain
  $host.UI.RawUI.ForegroundColor = "Cyan"
  Receive-Job -Name LitteBotServer
  Start-Sleep -Seconds 0.01
  If ($Host.UI.RawUI.KeyAvailable -and ($Key = $Host.UI.RawUI.ReadKey("AllowCtrlC,NoEcho,IncludeKeyUp"))) {
    If ([Int]$Key.Character -eq 3) {
      $host.UI.RawUI.ForegroundColor = "White"
      echo "Shutting down"
      Stop-Job -Name LitteBotEditor
      Stop-Job -Name LitteBotBrain
      Stop-Job -Name LitteBotServer
      Stop-Job -Name LitteBotSound
      Remove-Job -Name LitteBotEditor
      Remove-Job -Name LitteBotBrain
      Remove-Job -Name LitteBotServer
      Remove-Job -Name LitteBotSound
    }
  }
}

$host.UI.RawUI.ForegroundColor = "White"
[Console]::TreatControlCAsInput = $False
echo "End"
