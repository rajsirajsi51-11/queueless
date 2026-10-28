param([string]$BaseUrl='http://localhost:5000')
$health = Invoke-RestMethod "$BaseUrl/api/v1/health"
if (-not $health.ok) { throw 'Health check failed' }
Write-Host "PASS: $BaseUrl/api/v1/health"
