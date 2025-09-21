# setup-simics-device.ps1 - Initialize Simics device model project
# Usage: setup-simics-device.ps1 -Json "{device_description}"

param(
    [Parameter(Mandatory=$false)]
    [string]$Json = "",
    
    [Parameter(Mandatory=$false)]
    [string]$DeviceDescription = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Debug = $false
)

# Function to log debug messages
function Write-DebugLog {
    param([string]$Message)
    if ($Debug) {
        Write-Host "[DEBUG] $Message" -ForegroundColor Gray
    }
}

# Function to generate unique branch name
function Generate-BranchName {
    param([string]$DeviceName)
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    $randomSuffix = Get-Random -Minimum 100 -Maximum 999
    $cleanName = $DeviceName.ToLower() -replace '[^a-z0-9]', '-' -replace '--+', '-' -replace '^-|-$', ''
    return "$timestamp-$cleanName-$randomSuffix"
}

# Function to extract device name from description
function Extract-DeviceName {
    param([string]$Description)
    
    $Description = $Description.ToLower()
    
    if ($Description -match "uart|serial") { return "uart-controller" }
    elseif ($Description -match "timer") { return "timer-device" }
    elseif ($Description -match "interrupt|irq") { return "interrupt-controller" }
    elseif ($Description -match "memory|ddr|ram") { return "memory-controller" }
    elseif ($Description -match "ethernet|network") { return "network-controller" }
    elseif ($Description -match "gpio") { return "gpio-controller" }
    elseif ($Description -match "i2c") { return "i2c-controller" }
    elseif ($Description -match "spi") { return "spi-controller" }
    else {
        # Fallback: extract first meaningful word
        $words = $Description -split '\s+' | Where-Object { $_ -ne '' }
        if ($words.Count -gt 0) {
            $firstWord = $words[0] -replace '[^a-z0-9]', ''
            if ($firstWord) { return $firstWord }
        }
        return "generic-device"
    }
}

# Function to determine device type from description
function Determine-DeviceType {
    param([string]$Description)
    
    $Description = $Description.ToLower()
    
    if ($Description -match "processor|cpu|core") { return "processor" }
    elseif ($Description -match "memory|ddr|ram|cache") { return "memory" }
    elseif ($Description -match "uart|serial|i2c|spi|gpio") { return "peripheral" }
    elseif ($Description -match "interrupt|irq") { return "controller" }
    elseif ($Description -match "timer|clock") { return "timing" }
    elseif ($Description -match "network|ethernet") { return "network" }
    else { return "generic" }
}

# Function to determine Simics version
function Determine-SimicsVersion {
    # In a real implementation, this could check for installed Simics versions
    return "6.0"
}

# Main execution
function Main {
    Write-DebugLog "Starting Simics device project setup"
    
    # Determine device description from parameters
    $deviceDescription = ""
    if ($Json) {
        $deviceDescription = $Json
        Write-DebugLog "Using JSON parameter: $Json"
    } elseif ($DeviceDescription) {
        $deviceDescription = $DeviceDescription
        Write-DebugLog "Using DeviceDescription parameter: $DeviceDescription"
    }
    
    if (-not $deviceDescription) {
        if ($Json -ne $null) {
            $errorResult = @{
                error = "No device description provided"
                success = $false
            } | ConvertTo-Json -Compress
            Write-Output $errorResult
            exit 1
        } else {
            Write-Error "No device description provided"
            exit 1
        }
    }
    
    Write-DebugLog "Device description: $deviceDescription"
    
    # Extract device information
    $deviceName = Extract-DeviceName $deviceDescription
    $deviceType = Determine-DeviceType $deviceDescription
    $simicsVersion = Determine-SimicsVersion
    $branchName = Generate-BranchName $deviceName
    
    Write-DebugLog "Extracted device name: $deviceName"
    Write-DebugLog "Determined device type: $deviceType"
    Write-DebugLog "Generated branch name: $branchName"
    
    # Create project directory structure
    $projectRoot = Get-Location
    $specsDir = Join-Path $projectRoot "specs\$branchName"
    $specFile = Join-Path $specsDir "spec.md"
    $contractsDir = Join-Path $specsDir "contracts"
    $simicsDir = Join-Path $specsDir "simics"
    $implDetailsDir = Join-Path $specsDir "implementation-details"
    
    Write-DebugLog "Creating directory structure"
    New-Item -ItemType Directory -Force -Path $specsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $contractsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $simicsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $implDetailsDir | Out-Null
    
    # Create git branch if in a git repository
    if (Test-Path ".git") {
        Write-DebugLog "Creating git branch: $branchName"
        try {
            git checkout -b $branchName 2>$null
        } catch {
            # Ignore errors if branch creation fails
        }
    }
    
    # Initialize spec file with template header
    $currentDate = Get-Date -Format "yyyy-MM-dd"
    $specContent = @"
# Device Model Specification: $deviceName

**Feature Branch**: ``$branchName``  
**Created**: $currentDate  
**Status**: Draft  
**Input**: Device description: "$deviceDescription"

<!-- This file will be populated by the simics-device command -->
<!-- Template: templates/simics/projects/device-spec-template.md -->

"@
    
    Set-Content -Path $specFile -Value $specContent -Encoding UTF8
    Write-DebugLog "Created spec file: $specFile"
    
    # Create placeholder contract files
    Set-Content -Path "$contractsDir\register-interface.md" -Value "# Register Interface Specification" -Encoding UTF8
    Set-Content -Path "$contractsDir\memory-interface.md" -Value "# Memory Interface Specification" -Encoding UTF8
    Set-Content -Path "$contractsDir\simics-interface.md" -Value "# Simics Interface Specification" -Encoding UTF8
    
    # Create placeholder simics files
    Set-Content -Path "$simicsDir\device-config.md" -Value "# Device Configuration Specification" -Encoding UTF8
    Set-Content -Path "$simicsDir\integration-tests.md" -Value "# Integration Test Scenarios" -Encoding UTF8
    
    # Create placeholder implementation details
    Set-Content -Path "$implDetailsDir\dml-specification.md" -Value "# DML Implementation Specification" -Encoding UTF8
    Set-Content -Path "$implDetailsDir\python-interface.md" -Value "# Python Interface Implementation" -Encoding UTF8
    Set-Content -Path "$implDetailsDir\performance-targets.md" -Value "# Performance and Timing Requirements" -Encoding UTF8
    
    Write-DebugLog "Created project structure successfully"
    
    # Output results
    if ($Json -ne $null) {
        $result = @{
            success = $true
            branch_name = $branchName
            spec_file = $specFile
            device_name = $deviceName
            device_type = $deviceType
            simics_version = $simicsVersion
            specs_dir = $specsDir
            contracts_dir = $contractsDir
            simics_dir = $simicsDir
            implementation_details_dir = $implDetailsDir
        } | ConvertTo-Json -Compress
        Write-Output $result
    } else {
        Write-Host "Simics device project created successfully!" -ForegroundColor Green
        Write-Host "Branch: $branchName"
        Write-Host "Device: $deviceName ($deviceType)"
        Write-Host "Spec file: $specFile"
        Write-Host "Ready for specification generation."
    }
}

# Run main function
Main