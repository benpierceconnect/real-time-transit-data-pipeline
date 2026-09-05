# Security Policy

## Secrets

Never commit:

- `.env`
- passwords
- API keys or access tokens
- private keys
- cloud credentials
- private datasets
- personal records

Use `.env.example` only as a template and place real local values in an ignored `.env` file.

## Before the first public push

Run:

```bash
python scripts/secret_scan.py --public-files
python scripts/validate_project.py
pytest -q
```

Check the actual committed public file set before pushing. The initial release review accepted a scan of the sole initial commit's archived file contents; it was not an exhaustive Git-object audit. For later or imported history, use a history-aware secret scanner as well. If a real secret was ever committed, rotate it even after removing the text.

## Historical credentials

Historical credentials from earlier private work are not included in this release. Ben confirmed that the historical database password will never be reused and that the historical Mapbox token is revoked or permanently inactive. New local credentials belong only in the ignored `.env`.

## Reporting

Report a suspected security issue privately to `benpierceconnect@gmail.com` rather than opening a public issue containing sensitive details.
