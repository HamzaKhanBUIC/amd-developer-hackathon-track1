$ErrorActionPreference = "Stop"

# Pull the latest image
Write-Host "Pulling the latest image from ghcr.io..."
docker pull ghcr.io/hamzakhanbuic/amd-developer-hackathon-track1:latest

# Make sure the input file exists
if (!(Test-Path "input\tasks.json")) {
    Write-Host "input\tasks.json not found! Copying from test_tasks.json..."
    if (Test-Path "test_tasks.json") {
        Copy-Item -Path "test_tasks.json" -Destination "input\tasks.json"
    } else {
        Write-Host "Creating a dummy tasks.json..."
        '[{ "id": "t1", "prompt": "Solve math: 1+1" }, { "id": "t2", "prompt": "Code a loop in Python" }, { "id": "t3", "prompt": "Analyze sentiment: Bad!" }]' | Out-File -FilePath "input\tasks.json" -Encoding utf8
    }
}

# Run the docker container
Write-Host "Running the image (make sure FIREWORKS_API_KEY is set in your environment)..."
docker run --rm `
  -v "$PWD\input:/input" `
  -v "$PWD\output:/output" `
  -e FIREWORKS_API_KEY=$env:FIREWORKS_API_KEY `
  -e ALLOWED_MODELS="gemma-4-31b-it, gemma-4-26b-a4b-it, gemma-4-31b-it-nvfp4, kimi-k2p7-code, minimax-m3" `
  ghcr.io/hamzakhanbuic/amd-developer-hackathon-track1:latest

Write-Host "Execution complete! Check the output directory for results.json."
