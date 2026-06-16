"""
Main application entry point
Orchestrates system startup and configuration
"""
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('noahubai.log')
    ]
)

logger = logging.getLogger(__name__)


def print_banner():
    """Print ASCII banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                    🤖 NOAHUBAI 🤖                         ║
    ║     Unified AI with Memory, Issues, and Auto-Fixing       ║
    ║                                                           ║
    ║  • Continuous Learning & Memory Management              ║
    ║  • Intelligent Issue Detection & Tracking               ║
    ║  • Automated Problem Resolution                         ║
    ║  • Multi-Agent Architecture (Fully Detached)            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main entry point"""
    print_banner()
    
    logger.info("Noahubai is starting...")
    logger.info(f"Project root: {project_root}")
    
    # Import and run the server
    try:
        from backend.server import app
        import uvicorn
        
        logger.info("Starting FastAPI server...")
        logger.info("📡 Server running on http://0.0.0.0:8000")
        logger.info("📚 API docs available at http://localhost:8000/docs")
        logger.info("🔥 WebSocket available at ws://localhost:8000/ws")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
