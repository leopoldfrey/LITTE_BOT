#!/usr/bin/env pwsh
[Console]::TreatControlCAsInput = $True
# [System.Environment]::OSVersion.Platform

$host.UI.RawUI.ForegroundColor = "Red"
echo "Starting Led"
$job2 = Start-Job -Name LitteBotLed -WorkingDirectory $PWD/LitteBotLed -ScriptBlock {
   node ./ledCtrl.js
}

$host.UI.RawUI.ForegroundColor = "Magenta"
echo "Starting Sound"
$job3 = Start-Job -Name LitteBotSound -WorkingDirectory $PWD/LitteBotServer -ScriptBlock {
   python3 ./LitteBotSound.py
}

#$host.UI.RawUI.ForegroundColor = "Yellow"
#echo "Starting Simple Brain"
#$job2 = Start-Job -Name BotoBrain -WorkingDirectory $PWD/LitteBotServer -ScriptBlock {
#   python3 ./BotoBrain.py
#}

$host.UI.RawUI.ForegroundColor = "Cyan"
echo "Starting Simple Server"
$job5 = Start-Job -Name LitteBotServer  -WorkingDirectory $PWD/LitteBotServer -ScriptBlock {
  #Start-Sleep -Seconds 25;
  python3 ./LitteBotServerSimple.py
}

While (Get-Job -State "Running")
{
  $host.UI.RawUI.ForegroundColor = "Red"
  Receive-Job -Name LitteBotLed
  $host.UI.RawUI.ForegroundColor = "Magenta"
  Receive-Job -Name LitteBotSound
  #$host.UI.RawUI.ForegroundColor = "Yellow"
  #Receive-Job -Name BotoBrain
  $host.UI.RawUI.ForegroundColor = "White"
  Receive-Job -Name LitteBotServer
  Start-Sleep -Seconds 0.01
  If ($Host.UI.RawUI.KeyAvailable -and ($Key = $Host.UI.RawUI.ReadKey("AllowCtrlC,NoEcho,IncludeKeyUp"))) {
    If ([Int]$Key.Character -eq 3) {
      $host.UI.RawUI.ForegroundColor = "White"
      echo "Shutting down"
      Stop-Job -Name LitteBotServer
      #Stop-Job -Name BotoBrain
      Stop-Job -Name LitteBotLed
      Stop-Job -Name LitteBotSound
      Remove-Job -Name LitteBotServer
      #Remove-Job -Name BotoBrain
      Remove-Job -Name LitteBotLed
      Remove-Job -Name LitteBotSound
    }
  }
}

$host.UI.RawUI.ForegroundColor = "White"
[Console]::TreatControlCAsInput = $False
echo "End"
