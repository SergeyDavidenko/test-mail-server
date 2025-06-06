#!/usr/bin/env python3
"""
Entry point for Test Mail Server
"""

if __name__ == "__main__":
    from app.main import app
    import uvicorn
    from app.config import config

    # Run the server
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.API_PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
        access_log=True
    )
