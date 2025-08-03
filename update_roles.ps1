#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Vessel Guard User Role Management Script
.DESCRIPTION
    This script manages user roles and permissions in the Vessel Guard platform.
    It can create, update, and assign roles to users through the API.
.PARAMETER Action
    Action to perform: 'list', 'create', 'update', 'assign', 'remove'
.PARAMETER Username
    Target username for role operations
.PARAMETER Role
    Role name: 'viewer', 'engineer', 'organization_admin', 'super_admin'
.PARAMETER ApiUrl
    API base URL (default: http://localhost:8000)
.PARAMETER Token
    Admin authentication token
.EXAMPLE
    .\update_roles.ps1 -Action list
    .\update_roles.ps1 -Action assign -Username john.doe -Role engineer
    .\update_roles.ps1 -Action create -Role senior_engineer
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('list', 'create', 'update', 'assign', 'remove', 'show')]
    [string]$Action,
    
    [Parameter()]
    [string]$Username,
    
    [Parameter()]
    [ValidateSet('viewer', 'engineer', 'organization_admin', 'super_admin', 'senior_engineer')]
    [string]$Role,
    
    [Parameter()]
    [string]$ApiUrl = "http://localhost:8000",
    
    [Parameter()]
    [string]$Token,
    
    [Parameter()]
    [string]$OrganizationId
)

# Error handling
$ErrorActionPreference = "Stop"

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Cyan = "`e[36m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param($Message, $Color = $Reset)
    Write-Host "$Color$Message$Reset"
}

function Write-Success {
    param($Message)
    Write-ColorOutput "✅ $Message" $Green
}

function Write-Warning {
    param($Message)
    Write-ColorOutput "⚠️  $Message" $Yellow
}

function Write-Error {
    param($Message)
    Write-ColorOutput "❌ $Message" $Red
}

function Write-Info {
    param($Message)
    Write-ColorOutput "ℹ️  $Message" $Blue
}

function Get-AuthToken {
    if ($Token) {
        return $Token
    }
    
    # Try to get token from environment
    $envToken = $env:VESSEL_GUARD_TOKEN
    if ($envToken) {
        return $envToken
    }
    
    # Prompt for credentials
    Write-Info "Authentication required"
    $username = Read-Host "Username"
    $password = Read-Host "Password" -AsSecureString
    $passwordText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
    
    try {
        $loginBody = @{
            username = $username
            password = $passwordText
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$ApiUrl/api/v1/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
        return $response.access_token
    } catch {
        Write-Error "Authentication failed: $($_.Exception.Message)"
        exit 1
    }
}

function Invoke-ApiRequest {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [string]$AuthToken
    )
    
    $headers = @{
        "Authorization" = "Bearer $AuthToken"
        "Content-Type" = "application/json"
    }
    
    $uri = "$ApiUrl/api/v1$Endpoint"
    
    try {
        if ($Body) {
            $jsonBody = $Body | ConvertTo-Json -Depth 10
            $response = Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers -Body $jsonBody
        } else {
            $response = Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers
        }
        return $response
    } catch {
        Write-Error "API request failed: $($_.Exception.Message)"
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Error "Response: $responseBody"
        }
        throw
    }
}

function Show-Users {
    param([string]$AuthToken)
    
    Write-Info "Fetching user list..."
    
    $users = Invoke-ApiRequest -Endpoint "/users" -AuthToken $AuthToken
    
    if ($users.Count -eq 0) {
        Write-Warning "No users found"
        return
    }
    
    Write-ColorOutput "`n👥 Users List" $Cyan
    Write-ColorOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" $Cyan
    
    $users | ForEach-Object {
        $statusIcon = if ($_.is_active) { "🟢" } else { "🔴" }
        $roleColor = switch ($_.role) {
            "super_admin" { $Red }
            "organization_admin" { $Yellow }
            "engineer" { $Blue }
            "viewer" { $Reset }
            default { $Reset }
        }
        
        Write-Host "$statusIcon " -NoNewline
        Write-ColorOutput "$($_.username)" $Reset -NoNewline
        Write-Host " | " -NoNewline
        Write-ColorOutput "$($_.role)" $roleColor -NoNewline
        Write-Host " | " -NoNewline
        Write-Host "$($_.email)" -NoNewline
        if ($_.organization_name) {
            Write-Host " | " -NoNewline
            Write-ColorOutput "$($_.organization_name)" $Cyan
        } else {
            Write-Host ""
        }
    }
}

function Show-Roles {
    param([string]$AuthToken)
    
    Write-Info "Available roles in Vessel Guard:"
    
    $roles = @(
        @{ Name = "viewer"; Description = "Read-only access to projects and reports"; Icon = "👁️" }
        @{ Name = "engineer"; Description = "Create and manage engineering calculations"; Icon = "🔧" }
        @{ Name = "organization_admin"; Description = "Manage organization users and settings"; Icon = "👑" }
        @{ Name = "super_admin"; Description = "Full system administration access"; Icon = "🚀" }
    )
    
    Write-ColorOutput "`n🎭 Available Roles" $Cyan
    Write-ColorOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" $Cyan
    
    $roles | ForEach-Object {
        Write-Host "$($_.Icon) " -NoNewline
        Write-ColorOutput "$($_.Name)" $Yellow -NoNewline
        Write-Host " - $($_.Description)"
    }
}

function Assign-UserRole {
    param(
        [string]$Username,
        [string]$Role,
        [string]$AuthToken
    )
    
    if (!$Username -or !$Role) {
        Write-Error "Username and Role are required for role assignment"
        exit 1
    }
    
    Write-Info "Assigning role '$Role' to user '$Username'..."
    
    # First, get the user ID
    $users = Invoke-ApiRequest -Endpoint "/users" -AuthToken $AuthToken
    $targetUser = $users | Where-Object { $_.username -eq $Username }
    
    if (!$targetUser) {
        Write-Error "User '$Username' not found"
        exit 1
    }
    
    # Update user role
    $updateBody = @{
        role = $Role
    }
    
    try {
        $result = Invoke-ApiRequest -Endpoint "/users/$($targetUser.id)" -Method "PATCH" -Body $updateBody -AuthToken $AuthToken
        Write-Success "Successfully assigned role '$Role' to user '$Username'"
        
        # Show updated user info
        Write-Info "Updated user information:"
        Write-Host "Username: " -NoNewline
        Write-ColorOutput "$($result.username)" $Cyan
        Write-Host "Role: " -NoNewline
        Write-ColorOutput "$($result.role)" $Yellow
        Write-Host "Email: " -NoNewline
        Write-ColorOutput "$($result.email)" $Reset
        
    } catch {
        Write-Error "Failed to assign role: $($_.Exception.Message)"
        exit 1
    }
}

function Remove-UserRole {
    param(
        [string]$Username,
        [string]$AuthToken
    )
    
    if (!$Username) {
        Write-Error "Username is required for role removal"
        exit 1
    }
    
    Write-Warning "This will set the user role to 'viewer' (minimum role)"
    $confirm = Read-Host "Continue? (y/N)"
    
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Info "Operation cancelled"
        return
    }
    
    Assign-UserRole -Username $Username -Role "viewer" -AuthToken $AuthToken
}

function Show-UserDetails {
    param(
        [string]$Username,
        [string]$AuthToken
    )
    
    if (!$Username) {
        Write-Error "Username is required"
        exit 1
    }
    
    Write-Info "Fetching details for user '$Username'..."
    
    $users = Invoke-ApiRequest -Endpoint "/users" -AuthToken $AuthToken
    $user = $users | Where-Object { $_.username -eq $Username }
    
    if (!$user) {
        Write-Error "User '$Username' not found"
        exit 1
    }
    
    Write-ColorOutput "`n👤 User Details: $Username" $Cyan
    Write-ColorOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" $Cyan
    
    $statusIcon = if ($user.is_active) { "🟢 Active" } else { "🔴 Inactive" }
    $roleIcon = switch ($user.role) {
        "super_admin" { "🚀" }
        "organization_admin" { "👑" }
        "engineer" { "🔧" }
        "viewer" { "👁️" }
        default { "❓" }
    }
    
    Write-Host "ID: " -NoNewline
    Write-ColorOutput "$($user.id)" $Yellow
    
    Write-Host "Email: " -NoNewline
    Write-ColorOutput "$($user.email)" $Reset
    
    Write-Host "Role: " -NoNewline
    Write-ColorOutput "$roleIcon $($user.role)" $Yellow
    
    Write-Host "Status: " -NoNewline
    Write-ColorOutput "$statusIcon" $Green
    
    if ($user.organization_name) {
        Write-Host "Organization: " -NoNewline
        Write-ColorOutput "$($user.organization_name)" $Cyan
    }
    
    if ($user.created_at) {
        Write-Host "Created: " -NoNewline
        Write-ColorOutput "$($user.created_at)" $Reset
    }
}

# Main execution
try {
    Write-ColorOutput "`n🎭 Vessel Guard Role Management" $Cyan
    Write-ColorOutput "Action: $Action" $Blue
    Write-ColorOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" $Blue
    
    # Get authentication token
    $authToken = Get-AuthToken
    Write-Success "Authentication successful"
    
    # Execute the requested action
    switch ($Action) {
        "list" {
            Show-Users -AuthToken $authToken
        }
        "create" {
            Show-Roles -AuthToken $authToken
            Write-Warning "Role creation requires database-level changes"
            Write-Info "Available roles are built into the system"
        }
        "update" {
            Show-Roles -AuthToken $authToken
            Write-Warning "Role updates require code changes in the backend"
            Write-Info "Use 'assign' action to change user roles"
        }
        "assign" {
            Assign-UserRole -Username $Username -Role $Role -AuthToken $authToken
        }
        "remove" {
            Remove-UserRole -Username $Username -AuthToken $authToken
        }
        "show" {
            if ($Username) {
                Show-UserDetails -Username $Username -AuthToken $authToken
            } else {
                Show-Roles -AuthToken $authToken
            }
        }
    }
    
    Write-ColorOutput "`n✅ Role management operation completed successfully!" $Green
    
} catch {
    Write-Error "Operation failed: $($_.Exception.Message)"
    exit 1
}
