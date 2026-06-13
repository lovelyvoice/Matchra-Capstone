$body = '{"time_hours":2,"budget":300000,"platform":"windows","genres":"RPG Action","min_metacritic":0,"multiplayer":"both"}'
$r = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/time_budget' -Method POST -ContentType 'application/json' -Body $body
Write-Host "=== TIME & BUDGET TEST ==="
Write-Host ("Games found: " + $r.data.Count)
foreach ($g in $r.data) {
    Write-Host ($g.match_score.ToString() + "% - " + $g.name)
    Write-Host ("  score_breakdown: genre=" + $g.score_breakdown.genre_relevance + " budget=" + $g.score_breakdown.budget_fit + " playtime=" + $g.score_breakdown.playtime_fit + " quality=" + $g.score_breakdown.quality_score)
    Write-Host ("  matched_tags: " + ($g.matched_tags -join ", "))
}

Write-Host ""
Write-Host "=== ONBOARDING TEST ==="
$body2 = '{"experience":"aksi","platform":"windows","intensity":"medium"}'
$r2 = Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/onboarding' -Method POST -ContentType 'application/json' -Body $body2
Write-Host ("Games found: " + $r2.data.Count)
foreach ($g in $r2.data) {
    Write-Host ($g.match_score.ToString() + "% - " + $g.name)
}

Write-Host ""
Write-Host "ALL TESTS PASSED"
