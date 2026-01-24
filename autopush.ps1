$intervalSeconds = 1200 # 20 minutes

Write-Host "Starting Auto-Push Monitor for $(Get-Location)"
Write-Host "Checking every $intervalSeconds seconds..."

while ($true) {
    try {
        $status = git status --porcelain
        if ($status) {
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            Write-Host "[$timestamp] Changes detected. Staging..."
            git add .
            
            # Get the diff (larger limit to give more context)
            $diff = git diff --cached | Select-Object -First 200 | Out-String
            
            $commitMessage = "Auto-save: $timestamp"
            
            try {
                if ($diff) {
                    Write-Host "Generating commit message with Gemini..."
                    # Escape quotes in diff for the command line
                    $escapedDiff = $diff.Replace('"', '\"')
                    # Use a strict format to separate the message from logs
                    $prompt = "Generate a single, concise git commit message (max 1 line) for these changes. Start your response with 'COMMIT_MSG: ' followed immediately by the message. Return ONLY that line. Changes: $escapedDiff"
                    
                    # Call gemini CLI and capture all streams, joining them into a string
                    $geminiMsg = gemini prompt "$prompt" 2>&1 | Out-String
                    
                    if ($LASTEXITCODE -eq 0 -and !([string]::IsNullOrWhiteSpace($geminiMsg))) {
                        # Look for the specific marker to ignore logs like "Loaded cached credentials"
                        $match = $geminiMsg | Select-String -Pattern "COMMIT_MSG: (.*)"
                        if ($match) {
                            $commitMessage = $match.Matches.Groups[1].Value.Trim()
                            Write-Host "Generated Message: $commitMessage"
                        }
                        else {
                            Write-Host "Could not find COMMIT_MSG marker. Full output was:"
                            Write-Host $geminiMsg
                            Write-Host "Using default message."
                        }
                    }
                    else {
                        Write-Host "Gemini generation failed or empty. Output was:"
                        Write-Host $geminiMsg
                        Write-Host "Using default message."
                    }
                }
            }
            catch {
                Write-Host "Error generating message: $_"
            }

            Write-Host "[$timestamp] Committing..."
            git commit -m "$commitMessage"
            
            Write-Host "[$timestamp] Pushing to remote..."
            git push
            
            Write-Host "[$timestamp] Done."
        }
        else {
            Write-Host "No changes detected. Waiting..." -NoNewline
            Write-Host "`r" -NoNewline
        }
    }
    catch {
        Write-Host "An error occurred: $_"
    }
    
    Start-Sleep -Seconds $intervalSeconds
}
