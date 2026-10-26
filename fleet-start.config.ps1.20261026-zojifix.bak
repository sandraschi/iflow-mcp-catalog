# Per-repo fleet start config for iflow-mcp-catalog
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'iflow-mcp-catalog'
    BackendPort  = 10809
    FrontendPort = 10808
    HealthPath   = '/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind = 'none'
    }
    Frontend = @{
        Kind = 'none'
    }
}
