Write-Host "Testing Patient Prescription API..." -ForegroundColor Cyan
Write-Host ""

$patientId = "P1234511111111123"

Write-Host "Testing for Patient ID: $patientId" -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/get_patient_prescriptions/$patientId" -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Yellow
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
