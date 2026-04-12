[CmdletBinding()]
param(
  [string]$Message = '',
  [string]$Channel = '',
  [string]$TaskNumber = '',
  [string]$Duration = '',
  [string]$BotName = ''
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $PSCommandPath
$ConfigPath = Join-Path $ScriptDir 'notify-config.json'

function Get-AncestorDotEnvPaths {
  param([Parameter(Mandatory = $true)][string]$StartPath)

  $current = (Resolve-Path -LiteralPath $StartPath).Path
  $paths = [System.Collections.Generic.List[string]]::new()
  while ($true) {
    $candidate = Join-Path $current '.env'
    if (Test-Path -LiteralPath $candidate) {
      $paths.Add($candidate)
    }

    $parent = Split-Path -Parent $current
    if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $current) {
      break
    }
    $current = $parent
  }

  return $paths
}

function Get-DotEnvValue {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$Key
  )

  foreach ($line in [System.IO.File]::ReadAllLines($Path)) {
    $trimmed = $line.Trim()
    if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
    if ($trimmed.StartsWith('#')) { continue }

    if ($trimmed -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$') {
      $candidateKey = $Matches[1]
      if ($candidateKey -ne $Key) { continue }

      $value = $Matches[2].Trim()
      if (
        ($value.StartsWith('"') -and $value.EndsWith('"')) -or
        ($value.StartsWith("'") -and $value.EndsWith("'"))
      ) {
        $value = $value.Substring(1, $value.Length - 2)
      }

      if ([string]::IsNullOrWhiteSpace($value)) {
        return $null
      }

      return $value
    }
  }

  return $null
}

function Get-DotEnvValueFromAncestors {
  param(
    [Parameter(Mandatory = $true)][string]$StartPath,
    [Parameter(Mandatory = $true)][string]$Key
  )

  foreach ($path in (Get-AncestorDotEnvPaths -StartPath $StartPath)) {
    $value = Get-DotEnvValue -Path $path -Key $Key
    if (-not [string]::IsNullOrWhiteSpace($value)) {
      return $value
    }
  }

  return $null
}

function Get-NotifySettingFromEnvLayers {
  param(
    [Parameter(Mandatory = $true)][string]$StartPath,
    [Parameter(Mandatory = $true)][string]$Key
  )

  $processValue = [System.Environment]::GetEnvironmentVariable($Key, 'Process')
  if (-not [string]::IsNullOrWhiteSpace($processValue)) {
    return $processValue.Trim()
  }

  return Get-DotEnvValueFromAncestors -StartPath $StartPath -Key $Key
}

function Get-ConfigValue {
  param(
    [Parameter(Mandatory = $true)][psobject]$Config,
    [Parameter(Mandatory = $true)][string]$Name
  )

  if ($null -eq $Config) {
    return $null
  }

  $property = $Config.PSObject.Properties[$Name]
  if ($null -eq $property) {
    return $null
  }

  $value = [string]$property.Value
  if ([string]::IsNullOrWhiteSpace($value)) {
    return $null
  }

  return $value.Trim()
}

function Format-Duration {
  param([string]$Raw)

  if ([string]::IsNullOrWhiteSpace($Raw)) {
    return $null
  }

  if ($Raw -match '^\d+$') {
    $total = [int]$Raw
    $hours = [math]::Floor($total / 3600)
    $minutes = [math]::Floor(($total % 3600) / 60)
    $seconds = $total % 60

    if ($hours -gt 0) {
      return ('{0}h {1}m' -f $hours, $minutes)
    }
    if ($minutes -gt 0) {
      return ('{0}m' -f $minutes)
    }
    return ('{0}s' -f $seconds)
  }

  return $Raw
}

function Ensure-BotPrefixedMessage {
  param(
    [Parameter(Mandatory = $true)][string]$Body,
    [Parameter(Mandatory = $true)][string]$ResolvedBotName
  )

  if ($Body -match '^\s*[^:]{1,80}:\s') {
    return $Body
  }

  return '{0}: {1}' -f $ResolvedBotName, $Body
}

if ([string]::IsNullOrWhiteSpace($Message)) {
  exit 0
}

$settingsStartPath = (Get-Location).Path

if ($Channel -and $Channel.StartsWith('@') -and [string]::IsNullOrWhiteSpace($BotName)) {
  $BotName = $Channel.Substring(1).Trim()
  $Channel = ''
}

$config = $null
if (Test-Path -LiteralPath $ConfigPath) {
  $config = Get-Content -Raw $ConfigPath | ConvertFrom-Json
}

if ([string]::IsNullOrWhiteSpace($TaskNumber)) {
  $TaskNumber = $env:AXOLYNC_TASK_NUMBER
}

if ($TaskNumber -and ($Message -eq 'starting' -or $Message -eq 'finished')) {
  $Message = '{0} [task {1}]' -f $Message, $TaskNumber
}

if ([string]::IsNullOrWhiteSpace($Duration)) {
  $Duration = $env:AXOLYNC_NOTIFY_DURATION
}

$durationText = Format-Duration -Raw $Duration
if ($durationText) {
  $Message = '{0} | {1}' -f $Message, $durationText
}

if ([string]::IsNullOrWhiteSpace($Channel)) {
  $Channel = Get-NotifySettingFromEnvLayers -StartPath $settingsStartPath -Key 'AXOLYNC_NOTIFY_CHANNEL'
}
if ([string]::IsNullOrWhiteSpace($Channel)) {
  $Channel = Get-ConfigValue -Config $config -Name 'channel'
}
if ([string]::IsNullOrWhiteSpace($Channel)) {
  exit 0
}

$baseUrl = Get-NotifySettingFromEnvLayers -StartPath $settingsStartPath -Key 'AXOLYNC_NOTIFY_BASE_URL'
if ([string]::IsNullOrWhiteSpace($baseUrl)) {
  $baseUrl = Get-ConfigValue -Config $config -Name 'baseUrl'
}
if ([string]::IsNullOrWhiteSpace($baseUrl)) {
  $baseUrl = 'https://ntfy.sh'
}

$resolvedBotName = $BotName
if ([string]::IsNullOrWhiteSpace($resolvedBotName)) {
  $resolvedBotName = Get-NotifySettingFromEnvLayers -StartPath $settingsStartPath -Key 'AXOLYNC_NOTIFY_BOT_NAME'
}
if ([string]::IsNullOrWhiteSpace($resolvedBotName)) {
  $resolvedBotName = Get-ConfigValue -Config $config -Name 'botName'
}
if ([string]::IsNullOrWhiteSpace($resolvedBotName)) {
  $resolvedBotName = 'Codex'
}

$Message = Ensure-BotPrefixedMessage -Body $Message -ResolvedBotName $resolvedBotName

$uri = '{0}/{1}' -f $baseUrl.TrimEnd('/'), $Channel

Add-Type -AssemblyName System.Net.Http
$client = [System.Net.Http.HttpClient]::new()
$content = [System.Net.Http.StringContent]::new($Message, [System.Text.Encoding]::UTF8, 'text/plain')

try {
  $response = $client.PostAsync($uri, $content).GetAwaiter().GetResult()
  $response.EnsureSuccessStatusCode() | Out-Null
} finally {
  if ($null -ne $response) {
    $response.Dispose()
  }
  $content.Dispose()
  $client.Dispose()
}
