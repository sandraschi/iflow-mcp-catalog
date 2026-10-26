# Per-repo fleet start config for iflow-mcp-catalog
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'iflow-mcp-catalog'
    BackendPort  = 10809
    FrontendPort = 10808
    HealthPath   = '/api/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'mcp_catalog.webapp_backend:app'
        SyncExtras    = @('dev')
        SyncOnStart   = $true
        Env           = @{ WEB_PORT = '10809' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
    }
}
