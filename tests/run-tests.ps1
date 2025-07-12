# Test runner script for Haystack RAG Helm chart (PowerShell version)
param(
    [switch]$SkipPrerequisites,
    [switch]$SkipLint,
    [switch]$SkipSchema,
    [switch]$SkipUnit,
    [switch]$SkipIntegration,
    [switch]$SkipCustomValues
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    # Check if Helm is installed
    try {
        $null = Get-Command helm -ErrorAction Stop
    }
    catch {
        Write-Error "Helm is not installed"
        exit 1
    }
    
    # Check if jq is installed
    try {
        $null = Get-Command jq -ErrorAction Stop
    }
    catch {
        Write-Warning "jq is not installed. Some tests may fail."
    }
    
    # Check if helm-unittest plugin is installed
    $plugins = helm plugin list 2>$null
    if ($plugins -notmatch "unittest") {
        Write-Status "Installing helm-unittest plugin..."
        helm plugin install https://github.com/quintush/helm-unittest
    }
    
    Write-Status "Prerequisites check completed"
}

# Run unit tests
function Test-UnitTests {
    Write-Status "Running unit tests..."
    try {
        helm unittest tests/unit/
        Write-Status "Unit tests passed"
        return $true
    }
    catch {
        Write-Error "Unit tests failed"
        return $false
    }
}

# Run integration tests
function Test-IntegrationTests {
    Write-Status "Running integration tests..."
    try {
        helm unittest tests/integration/
        Write-Status "Integration tests passed"
        return $true
    }
    catch {
        Write-Error "Integration tests failed"
        return $false
    }
}

# Run chart linting
function Test-Lint {
    Write-Status "Running Helm lint..."
    try {
        helm lint . --strict
        Write-Status "Helm lint passed"
        return $true
    }
    catch {
        Write-Error "Helm lint failed"
        return $false
    }
}

# Run schema validation
function Test-SchemaValidation {
    Write-Status "Running schema validation..."
    try {
        $null = Get-Command kubeconform -ErrorAction Stop
        helm template . | kubeconform -strict -summary -skip IngressRoute,Middleware,ServersTransport
        Write-Status "Schema validation passed"
        return $true
    }
    catch {
        Write-Warning "kubeconform not found, skipping schema validation"
        return $true
    }
}

# Test with custom values
function Test-CustomValues {
    Write-Status "Testing with custom values..."
    try {
        helm template test-release . -f tests/test-values.yaml | Out-Null
        Write-Status "Custom values test passed"
        return $true
    }
    catch {
        Write-Error "Custom values test failed"
        return $false
    }
}

# Generate test report
function New-TestReport {
    Write-Status "Generating test report..."
    try {
        helm unittest --output-type XUnit --output-file test-report.xml .
        if (Test-Path "test-report.xml") {
            Write-Status "Test report generated: test-report.xml"
        }
    }
    catch {
        Write-Warning "Failed to generate test report"
    }
}

# Main execution
function Main {
    Write-Status "Starting Helm chart tests..."
    
    # Change to chart directory
    Set-Location (Split-Path $PSScriptRoot -Parent)
    
    if (-not $SkipPrerequisites) {
        Test-Prerequisites
    }
    
    # Run tests
    $exitCode = 0
    
    if (-not $SkipLint) {
        if (-not (Test-Lint)) { $exitCode = 1 }
    }
    
    if (-not $SkipSchema) {
        if (-not (Test-SchemaValidation)) { $exitCode = 1 }
    }
    
    if (-not $SkipUnit) {
        if (-not (Test-UnitTests)) { $exitCode = 1 }
    }
    
    if (-not $SkipIntegration) {
        if (-not (Test-IntegrationTests)) { $exitCode = 1 }
    }
    
    if (-not $SkipCustomValues) {
        if (-not (Test-CustomValues)) { $exitCode = 1 }
    }
    
    New-TestReport
    
    if ($exitCode -eq 0) {
        Write-Status "All tests passed! 🎉"
    }
    else {
        Write-Error "Some tests failed! ❌"
    }
    
    exit $exitCode
}

# Run main function
Main 