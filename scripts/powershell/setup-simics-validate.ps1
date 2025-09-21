# setup-simics-validate.ps1 - Initialize Simics validation framework project
# Usage: setup-simics-validate.ps1 -Json "{validation_requirements}"

param(
    [Parameter(Mandatory=$false)]
    [string]$Json = "",
    
    [Parameter(Mandatory=$false)]
    [string]$ValidationRequirements = "",
    
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
    param([string]$ModelName)
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))
    $randomSuffix = Get-Random -Minimum 100 -Maximum 999
    $cleanName = $ModelName.ToLower() -replace '[^a-z0-9]', '-' -replace '--+', '-' -replace '^-|-$', ''
    return "$timestamp-validate-$cleanName-$randomSuffix"
}

# Function to extract model name from requirements
function Extract-ModelName {
    param([string]$Requirements)
    
    $Requirements = $Requirements.ToLower()
    
    if ($Requirements -match "uart|serial") { return "uart-controller" }
    elseif ($Requirements -match "timer") { return "timer-device" }
    elseif ($Requirements -match "platform|system") { return "virtual-platform" }
    elseif ($Requirements -match "processor|cpu") { return "processor-model" }
    elseif ($Requirements -match "memory|ddr") { return "memory-controller" }
    elseif ($Requirements -match "network|ethernet") { return "network-device" }
    else {
        # Fallback: extract first meaningful word
        $words = $Requirements -split '\s+' | Where-Object { $_ -ne '' }
        if ($words.Count -gt 0) {
            $firstWord = $words[0] -replace '[^a-z0-9]', ''
            if ($firstWord) { return $firstWord }
        }
        return "model"
    }
}

# Function to determine model type from requirements
function Determine-ModelType {
    param([string]$Requirements)
    
    $Requirements = $Requirements.ToLower()
    
    if ($Requirements -match "device|controller|peripheral") { return "device" }
    elseif ($Requirements -match "platform|system") { return "platform" }
    elseif ($Requirements -match "processor|cpu") { return "processor" }
    elseif ($Requirements -match "component|module") { return "component" }
    else { return "generic" }
}

# Function to determine validation scope from requirements
function Determine-ValidationScope {
    param([string]$Requirements)
    
    $Requirements = $Requirements.ToLower()
    $scopes = @()
    
    if ($Requirements -match "functional|function|behavior") { $scopes += "functional" }
    if ($Requirements -match "performance|speed|throughput|latency") { $scopes += "performance" }
    if ($Requirements -match "integration|system") { $scopes += "integration" }
    if ($Requirements -match "compliance|standard|specification") { $scopes += "compliance" }
    if ($Requirements -match "regression|compatibility") { $scopes += "regression" }
    if ($Requirements -match "stress|load|robustness") { $scopes += "stress" }
    
    # Default to functional if no specific scope identified
    if ($scopes.Count -eq 0) { $scopes += "functional" }
    
    return $scopes -join ","
}

# Function to extract test categories from requirements
function Extract-TestCategories {
    param([string]$Requirements)
    
    $Requirements = $Requirements.ToLower()
    $categories = @()
    
    if ($Requirements -match "unit|component") { $categories += "unit" }
    if ($Requirements -match "integration|interface") { $categories += "integration" }
    if ($Requirements -match "system|end.*to.*end") { $categories += "system" }
    if ($Requirements -match "acceptance|validation") { $categories += "acceptance" }
    if ($Requirements -match "performance|benchmark") { $categories += "performance" }
    if ($Requirements -match "security|safety") { $categories += "security" }
    
    # Default to basic categories if none identified
    if ($categories.Count -eq 0) { $categories += @("functional", "integration") }
    
    return $categories -join ","
}

# Main execution
function Main {
    Write-DebugLog "Starting Simics validation project setup"
    
    # Determine validation requirements from parameters
    $validationRequirements = ""
    if ($Json) {
        $validationRequirements = $Json
        Write-DebugLog "Using JSON parameter: $Json"
    } elseif ($ValidationRequirements) {
        $validationRequirements = $ValidationRequirements
        Write-DebugLog "Using ValidationRequirements parameter: $ValidationRequirements"
    }
    
    if (-not $validationRequirements) {
        if ($Json -ne $null) {
            $errorResult = @{
                error = "No validation requirements provided"
                success = $false
            } | ConvertTo-Json -Compress
            Write-Output $errorResult
            exit 1
        } else {
            Write-Error "No validation requirements provided"
            exit 1
        }
    }
    
    Write-DebugLog "Validation requirements: $validationRequirements"
    
    # Extract validation information
    $modelName = Extract-ModelName $validationRequirements
    $modelType = Determine-ModelType $validationRequirements
    $validationScope = Determine-ValidationScope $validationRequirements
    $testCategories = Extract-TestCategories $validationRequirements
    $branchName = Generate-BranchName $modelName
    
    Write-DebugLog "Extracted model name: $modelName"
    Write-DebugLog "Determined model type: $modelType"
    Write-DebugLog "Validation scope: $validationScope"
    Write-DebugLog "Test categories: $testCategories"
    Write-DebugLog "Generated branch name: $branchName"
    
    # Create project directory structure
    $projectRoot = Get-Location
    $specsDir = Join-Path $projectRoot "specs\$branchName"
    $specFile = Join-Path $specsDir "spec.md"
    $contractsDir = Join-Path $specsDir "contracts"
    $simicsDir = Join-Path $specsDir "simics"
    $implDetailsDir = Join-Path $specsDir "implementation-details"
    $testsDir = Join-Path $specsDir "tests"
    
    Write-DebugLog "Creating directory structure"
    New-Item -ItemType Directory -Force -Path $specsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $contractsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $simicsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $implDetailsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $testsDir | Out-Null
    
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
# Validation Framework: $modelName

**Feature Branch**: ``$branchName``  
**Created**: $currentDate  
**Status**: Draft  
**Input**: Validation requirements: "$validationRequirements"

<!-- This file will be populated by the simics-validate command -->
<!-- Template: templates/simics/projects/validation-template.md -->

"@
    
    Set-Content -Path $specFile -Value $specContent -Encoding UTF8
    Write-DebugLog "Created spec file: $specFile"
    
    # Create placeholder contract files
    Set-Content -Path "$contractsDir\test-interfaces.md" -Value "# Test Interface Specifications" -Encoding UTF8
    Set-Content -Path "$contractsDir\validation-criteria.md" -Value "# Validation Criteria Contracts" -Encoding UTF8
    Set-Content -Path "$contractsDir\test-environment.md" -Value "# Test Environment Contracts" -Encoding UTF8
    
    # Create placeholder simics files
    Set-Content -Path "$simicsDir\validation-config.md" -Value "# Validation Configuration Specification" -Encoding UTF8
    Set-Content -Path "$simicsDir\test-execution.md" -Value "# Test Execution Framework" -Encoding UTF8
    Set-Content -Path "$simicsDir\results-analysis.md" -Value "# Results Analysis and Reporting" -Encoding UTF8
    
    # Create placeholder implementation details
    Set-Content -Path "$implDetailsDir\test-implementation.md" -Value "# Test Implementation Specifications" -Encoding UTF8
    Set-Content -Path "$implDetailsDir\automation-framework.md" -Value "# Automation Framework Details" -Encoding UTF8
    Set-Content -Path "$implDetailsDir\performance-measurement.md" -Value "# Performance Measurement Details" -Encoding UTF8
    
    # Create placeholder test directories
    Set-Content -Path "$testsDir\functional-tests.md" -Value "# Functional Test Cases" -Encoding UTF8
    Set-Content -Path "$testsDir\performance-tests.md" -Value "# Performance Test Cases" -Encoding UTF8
    Set-Content -Path "$testsDir\integration-tests.md" -Value "# Integration Test Cases" -Encoding UTF8
    
    Write-DebugLog "Created project structure successfully"
    
    # Output results
    if ($Json -ne $null) {
        $result = @{
            success = $true
            branch_name = $branchName
            spec_file = $specFile
            model_name = $modelName
            model_type = $modelType
            validation_scope = $validationScope
            test_categories = $testCategories
            specs_dir = $specsDir
            contracts_dir = $contractsDir
            simics_dir = $simicsDir
            implementation_details_dir = $implDetailsDir
            tests_dir = $testsDir
        } | ConvertTo-Json -Compress
        Write-Output $result
    } else {
        Write-Host "Simics validation project created successfully!" -ForegroundColor Green
        Write-Host "Branch: $branchName"
        Write-Host "Model: $modelName ($modelType)"
        Write-Host "Validation Scope: $validationScope"
        Write-Host "Test Categories: $testCategories"
        Write-Host "Spec file: $specFile"
        Write-Host "Ready for validation framework specification."
    }
}

# Run main function
Main