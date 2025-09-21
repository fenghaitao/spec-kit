# setup-simics-platform.ps1 - Initialize Simics virtual platform project with workflow enforcement
# Usage: setup-simics-platform.ps1 -Json "{platform_description}"

param(
    [Parameter(Mandatory=$false)]
    [string]$Json = "",
    
    [Parameter(Mandatory=$false)]
    [string]$PlatformDescription = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Debug = $false
)

# Load common functions
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
. "$scriptDir\common.ps1"

# Function to initialize workflow enforcement
function Initialize-WorkflowEnforcement {
    Write-DebugLog "Initializing workflow enforcement for product phase"
    
    # Create .spec-kit directory structure
    $specKitDir = Join-Path (Get-Location) ".spec-kit"
    $phaseMarkersDir = Join-Path $specKitDir "phase-markers"
    
    New-Item -ItemType Directory -Force -Path $specKitDir | Out-Null
    New-Item -ItemType Directory -Force -Path $phaseMarkersDir | Out-Null
    
    # Initialize workflow state if not exists
    $stateFile = Join-Path $specKitDir "workflow-state.json"
    if (-not (Test-Path $stateFile)) {
        $featureName = Get-FeatureNameFromBranch
        $currentTime = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
        
        $initialState = @{
            currentPhase = "product"
            completedPhases = @()
            featureName = $featureName
            lastUpdated = $currentTime
            contextHash = $null
            phaseData = @{}
        } | ConvertTo-Json -Depth 3
        
        Set-Content -Path $stateFile -Value $initialState -Encoding UTF8
        Write-DebugLog "Created workflow state file: $stateFile"
    }
    
    # Clear any existing phase markers to start fresh
    Get-ChildItem -Path $phaseMarkersDir -Filter "*.complete" -ErrorAction SilentlyContinue | Remove-Item -Force
    
    Write-DebugLog "Workflow enforcement initialized"
}

# Function to extract feature name from git branch
function Get-FeatureNameFromBranch {
    if (Test-Path ".git") {
        try {
            $branchName = git branch --show-current 2>$null
            if ($branchName -and $branchName -match '^\d+-(.+)$') {
                return $matches[1]
            } elseif ($branchName) {
                return $branchName
            }
        } catch {
            # Ignore git errors
        }
    }
    return "unknown-feature"
}

# Function to capture product context for workflow
function Capture-ProductContext {
    param(
        [string]$PlatformName,
        [string]$PlatformType,
        [string]$PlatformDescription,
        [string]$ComponentList,
        [string]$TargetSystem
    )
    
    Write-DebugLog "Capturing product context for workflow transfer"
    
    # Create product context data structure
    $contextData = @{
        vision = "Virtual platform simulation for $PlatformName targeting $TargetSystem architecture"
        success_criteria = @(
            "Platform boots successfully in Simics",
            "All identified components are functional",
            "System meets target performance requirements",
            "Platform supports intended use cases"
        )
        constraints = @(
            "Must be compatible with Simics simulation environment",
            "Platform type: $PlatformType",
            "Target system: $TargetSystem",
            "Required components: $ComponentList"
        )
        stakeholders = @(
            @{name = "Platform Developer"; role = "Implementation and testing"},
            @{name = "System Architect"; role = "Architecture validation"},
            @{name = "Validation Engineer"; role = "Testing and verification"}
        )
        requirements = @(
            @{id = "REQ-001"; description = "Platform must support $TargetSystem instruction set"},
            @{id = "REQ-002"; description = "Must include essential components: $ComponentList"},
            @{id = "REQ-003"; description = "Platform configuration must be maintainable and extensible"}
        )
        metadata = @{
            platform_name = $PlatformName
            platform_type = $PlatformType
            target_system = $TargetSystem
            component_list = $ComponentList
            original_description = $PlatformDescription
            captured_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
        }
    }
    
    # Store context in workflow state
    $specKitDir = Join-Path (Get-Location) ".spec-kit"
    $stateFile = Join-Path $specKitDir "workflow-state.json"
    
    # Update workflow state with product context
    try {
        $state = Get-Content -Path $stateFile -Raw | ConvertFrom-Json
        if (-not $state.phaseData) {
            $state.phaseData = @{}
        }
        $state.phaseData | Add-Member -NotePropertyName "product" -NotePropertyValue $contextData -Force
        $state.lastUpdated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
        
        $updatedState = $state | ConvertTo-Json -Depth 5
        Set-Content -Path $stateFile -Value $updatedState -Encoding UTF8
    } catch {
        # Fallback if JSON processing fails
        Write-DebugLog "JSON processing failed, storing context as separate file"
        $contextJson = $contextData | ConvertTo-Json -Depth 3
        Set-Content -Path (Join-Path $specKitDir "product-context.json") -Value $contextJson -Encoding UTF8
    }
    
    Write-DebugLog "Product context captured and stored"
}

# Function to complete product phase
function Complete-ProductPhase {
    Write-DebugLog "Completing product phase"
    
    $specKitDir = Join-Path (Get-Location) ".spec-kit"
    $phaseMarkersDir = Join-Path $specKitDir "phase-markers"
    $stateFile = Join-Path $specKitDir "workflow-state.json"
    
    # Create product phase completion marker
    New-Item -ItemType File -Force -Path (Join-Path $phaseMarkersDir "product.complete") | Out-Null
    
    # Update workflow state
    try {
        $state = Get-Content -Path $stateFile -Raw | ConvertFrom-Json
        
        # Mark product phase as completed
        if ($state.completedPhases -notcontains "product") {
            $state.completedPhases += "product"
        }
        $state.currentPhase = $null
        $state.lastUpdated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
        
        $updatedState = $state | ConvertTo-Json -Depth 5
        Set-Content -Path $stateFile -Value $updatedState -Encoding UTF8
    } catch {
        Write-DebugLog "Failed to update workflow state"
    }
    
    Write-DebugLog "Product phase marked as complete"
}
function Write-DebugLog {
    param([string]$Message)
    if ($Debug) {
        Write-Host "[DEBUG] $Message" -ForegroundColor Gray
    }
}

# Function to generate unique branch name
function Generate-BranchName {
    param([string]$PlatformName)
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    $randomSuffix = Get-Random -Minimum 100 -Maximum 999
    $cleanName = $PlatformName.ToLower() -replace '[^a-z0-9]', '-' -replace '--+', '-' -replace '^-|-$', ''
    return "$timestamp-$cleanName-$randomSuffix"
}

# Function to extract platform name from description
function Extract-PlatformName {
    param([string]$Description)
    
    $Description = $Description.ToLower()
    
    if ($Description -match "arm|cortex") { return "arm-platform" }
    elseif ($Description -match "x86|intel") { return "x86-platform" }
    elseif ($Description -match "risc|riscv") { return "riscv-platform" }
    elseif ($Description -match "embedded|mcu") { return "embedded-platform" }
    elseif ($Description -match "server") { return "server-platform" }
    elseif ($Description -match "mobile|phone") { return "mobile-platform" }
    elseif ($Description -match "automotive|car") { return "automotive-platform" }
    elseif ($Description -match "iot") { return "iot-platform" }
    else {
        # Fallback: extract first meaningful word
        $words = $Description -split '\s+' | Where-Object { $_ -ne '' }
        if ($words.Count -gt 0) {
            $firstWord = $words[0] -replace '[^a-z0-9]', ''
            if ($firstWord) { return $firstWord }
        }
        return "generic-platform"
    }
}

# Function to determine platform type from description
function Determine-PlatformType {
    param([string]$Description)
    
    $Description = $Description.ToLower()
    
    if ($Description -match "server|datacenter") { return "server" }
    elseif ($Description -match "embedded|mcu|microcontroller") { return "embedded" }
    elseif ($Description -match "mobile|phone|tablet") { return "mobile" }
    elseif ($Description -match "automotive|car|vehicle") { return "automotive" }
    elseif ($Description -match "iot|sensor") { return "iot" }
    elseif ($Description -match "desktop|workstation") { return "desktop" }
    elseif ($Description -match "development|dev|prototype") { return "development" }
    else { return "generic" }
}

# Function to extract component list from description
function Extract-ComponentList {
    param([string]$Description)
    
    $Description = $Description.ToLower()
    $components = @()
    
    if ($Description -match "cpu|processor|core") { $components += "processor" }
    if ($Description -match "memory|ram|ddr") { $components += "memory" }
    if ($Description -match "uart|serial") { $components += "uart" }
    if ($Description -match "timer") { $components += "timer" }
    if ($Description -match "interrupt|irq") { $components += "interrupt-controller" }
    if ($Description -match "ethernet|network") { $components += "network" }
    if ($Description -match "gpio") { $components += "gpio" }
    if ($Description -match "i2c") { $components += "i2c" }
    if ($Description -match "spi") { $components += "spi" }
    
    return $components -join ","
}

# Function to determine target system from description
function Determine-TargetSystem {
    param([string]$Description)
    
    $Description = $Description.ToLower()
    
    if ($Description -match "arm.*cortex.*a[0-9]") { return "ARM Cortex-A" }
    elseif ($Description -match "arm.*cortex.*m[0-9]") { return "ARM Cortex-M" }
    elseif ($Description -match "x86.*64|amd64") { return "x86-64" }
    elseif ($Description -match "x86.*32|i386") { return "x86-32" }
    elseif ($Description -match "risc.*v") { return "RISC-V" }
    elseif ($Description -match "mips") { return "MIPS" }
    else { return "Generic" }
}

# Main execution
function Main {
    Write-DebugLog "Starting Simics platform project setup with workflow enforcement"
    
    # Determine platform description from parameters
    $platformDescription = ""
    if ($Json) {
        $platformDescription = $Json
        Write-DebugLog "Using JSON parameter: $Json"
    } elseif ($PlatformDescription) {
        $platformDescription = $PlatformDescription
        Write-DebugLog "Using PlatformDescription parameter: $PlatformDescription"
    }
    
    if (-not $platformDescription) {
        if ($Json -ne $null) {
            $errorResult = @{
                error = "No platform description provided"
                success = $false
            } | ConvertTo-Json -Compress
            Write-Output $errorResult
            exit 1
        } else {
            Write-Error "No platform description provided"
            exit 1
        }
    }
    
    Write-DebugLog "Platform description: $platformDescription"
    
    # Initialize workflow enforcement (Product Phase Entry Point)
    Initialize-WorkflowEnforcement
    
    # Extract platform information
    $platformName = Extract-PlatformName $platformDescription
    $platformType = Determine-PlatformType $platformDescription
    $componentList = Extract-ComponentList $platformDescription
    $targetSystem = Determine-TargetSystem $platformDescription
    $branchName = Generate-BranchName $platformName
    
    Write-DebugLog "Extracted platform name: $platformName"
    Write-DebugLog "Determined platform type: $platformType"
    Write-DebugLog "Component list: $componentList"
    Write-DebugLog "Target system: $targetSystem"
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
# Virtual Platform Specification: $platformName

**Feature Branch**: ``$branchName``  
**Created**: $currentDate  
**Status**: Draft  
**Input**: Platform description: "$platformDescription"

<!-- This file will be populated by the simics-platform command -->
<!-- Template: templates/simics/projects/platform-spec-template.md -->

"@
    
    Set-Content -Path $specFile -Value $specContent -Encoding UTF8
    Write-DebugLog "Created spec file: $specFile"
    
    # Create placeholder contract files
    Set-Content -Path "$contractsDir\system-architecture.md" -Value "# System Architecture Specification" -Encoding UTF8
    Set-Content -Path "$contractsDir\memory-map.md" -Value "# Memory Map Specification" -Encoding UTF8
    Set-Content -Path "$contractsDir\device-interfaces.md" -Value "# Device Interface Specifications" -Encoding UTF8
    
    # Create placeholder simics files
    Set-Content -Path "$simicsDir\platform-config.md" -Value "# Platform Configuration Specification" -Encoding UTF8
    Set-Content -Path "$simicsDir\integration-tests.md" -Value "# Integration Test Scenarios" -Encoding UTF8
    
    # Create placeholder implementation details
    Set-Content -Path "$implDetailsDir\system-configuration.md" -Value "# System Configuration Implementation" -Encoding UTF8
    Set-Content -Path "$implDetailsDir\device-instantiation.md" -Value "# Device Instantiation and Connection" -Encoding UTF8
    Set-Content -Path "$implDetailsDir\boot-sequence.md" -Value "# Boot Sequence and Initialization" -Encoding UTF8
    
    Write-DebugLog "Created project structure successfully"
    
    # Capture product context for workflow transfer
    Capture-ProductContext $platformName $platformType $platformDescription $componentList $targetSystem
    
    # Complete product phase
    Complete-ProductPhase
    
    # Output results with workflow enforcement information
    if ($Json -ne $null) {
        $result = @{
            success = $true
            branch_name = $branchName
            spec_file = $specFile
            platform_name = $platformName
            platform_type = $platformType
            component_list = $componentList
            target_system = $targetSystem
            specs_dir = $specsDir
            contracts_dir = $contractsDir
            simics_dir = $simicsDir
            implementation_details_dir = $implDetailsDir
            workflow = @{
                phase_completed = "product"
                next_phase = "specify"
                next_command = "/specify"
                enforcement_active = $true
                context_captured = $true
            }
        } | ConvertTo-Json -Compress
        Write-Output $result
    } else {
        Write-Host "Simics platform project created successfully!" -ForegroundColor Green
        Write-Host "Branch: $branchName"
        Write-Host "Platform: $platformName ($platformType)"
        Write-Host "Target System: $targetSystem"
        Write-Host "Components: $componentList"
        Write-Host "Spec file: $specFile"
        Write-Host ""
        Write-Host "=== WORKFLOW ENFORCEMENT ACTIVE ===" -ForegroundColor Yellow
        Write-Host "`u2713 Product phase completed successfully" -ForegroundColor Green
        Write-Host "`u2713 Product context captured for specification phase" -ForegroundColor Green
        Write-Host "`u2192 Next step: Use /specify command to proceed to specification phase" -ForegroundColor Cyan
        Write-Host "`u26a0 Attempting to skip to /plan or /tasks will be blocked until specification is completed" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Ready for specification generation."
    }
}

# Run main function
Main