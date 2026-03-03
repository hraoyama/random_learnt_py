fnm env --use-on-cd | Out-String | Invoke-Expression

function ca {
    param($VariableHere)
    conda activate "$VariableHere"
}

function grep {
  $input | Out-String -stream | Select-String $args
}

function history {
	Get-History
}

filter xargs { ($h,$t) = $args; & $h ($t + $_) }
