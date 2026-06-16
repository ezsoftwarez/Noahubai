#!/usr/bin/env python3
"""
Quick Start Script for Noahubai
Helps users get started with the system
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                   🤖 NOAHUBAI QUICK START GUIDE 🤖                           ║
║                                                                              ║
║                 Unified AI with Memory, Issues, and Auto-Fixing             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("""
📋 What is Noahubai?
═════════════════════════════════════════════════════════════════════════════

Noahubai is an intelligent AI system with three core capabilities:

  🧠 Memory Agent - Learns patterns and stores solutions
  🔍 Issue Agent - Detects and tracks all problems
  🔧 Fixer Agent - Automatically fixes issues

The system continuously learns and improves over time.

    """)
    
    print("""
🚀 Getting Started
═════════════════════════════════════════════════════════════════════════════

Choose your platform:

  1. Windows
     → Double-click: setup.bat
     → OR: python setup.py
  
  2. Linux/macOS
     → chmod +x setup.sh && ./setup.sh

The installer will:
  ✓ Create virtual environment
  ✓ Install dependencies
  ✓ Copy application files
  ✓ Create desktop shortcuts
  ✓ Generate configuration

    """)
    
    print("""
📖 Available Documentation
═════════════════════════════════════════════════════════════════════════════

  README.md - Quick start and overview
  COMPLETE_DOCUMENTATION.md - Full system guide
  SYSTEM_SUMMARY.md - Features and capabilities

    """)
    
    print("""
💡 Example API Calls
═════════════════════════════════════════════════════════════════════════════

1. Check system health:
   curl http://localhost:8000/api/health

2. Detect an issue:
   curl -X POST http://localhost:8000/api/issues/detect \\
     -H "Content-Type: application/json" \\
     -d '{"type":"timeout","message":"Request timeout","severity":"warning"}'

3. Learn a pattern:
   curl -X POST http://localhost:8000/api/memory/learn \\
     -H "Content-Type: application/json" \\
     -d '{"pattern_id":"cache-on-load","pattern_data":{"action":"enable_cache"}}'

4. Get growth metrics:
   curl http://localhost:8000/api/memory/growth

5. Interactive API docs:
   http://localhost:8000/docs

    """)
    
    print("""
🔧 Key Features
═════════════════════════════════════════════════════════════════════════════

✓ Continuous Learning - Gets smarter over time
✓ Issue Tracking - Never forgets a problem
✓ Auto-Fixing - Solves problems automatically
✓ Growth Metrics - Track system improvement
✓ Real-time Updates - WebSocket support
✓ REST API - 30+ endpoints
✓ Advanced Settings - Deep customization
✓ Backup/Restore - Settings management

    """)
    
    print("""
⚙️ System Requirements
═════════════════════════════════════════════════════════════════════════════

  • Python 3.10 or higher
  • 500MB disk space
  • 512MB RAM minimum
  • Windows, Linux, or macOS

    """)
    
    print("""
📞 Support & Resources
═════════════════════════════════════════════════════════════════════════════

  GitHub: https://github.com/ezsoftwarez/Noahubai
  Issues: Report bugs on GitHub
  Docs: See README.md and COMPLETE_DOCUMENTATION.md

    """)
    
    print("""
🎯 Next Steps
═════════════════════════════════════════════════════════════════════════════

1. Run installer:
   • Windows: python setup.py or setup.bat
   • Linux/macOS: ./setup.sh

2. Start application:
   • Windows: run_noahubai.bat
   • Linux/macOS: ./run_noahubai.sh

3. Open browser:
   → http://localhost:8000

4. Check dashboard and API docs

5. Begin using the system:
   • Detect issues
   • Learn patterns
   • Monitor growth
   • Watch automatic fixes

    """)
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              Thank you for choosing Noahubai! 🌟                             ║
║                                                                              ║
║        Growing smarter with every issue solved 🧠✨                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Ask if user wants to start installation
    try:
        response = input("Would you like to start installation now? (Y/n): ").strip().lower()
        
        if response != 'n':
            setup_file = None
            
            if sys.platform == "win32":
                setup_file = "setup.bat"
                if Path(setup_file).exists():
                    os.startfile(setup_file)
                else:
                    print(f"\n❌ {setup_file} not found")
                    print("Please run: python setup.py")
            else:
                setup_file = "setup.sh"
                if Path(setup_file).exists():
                    subprocess.run(["chmod", "+x", setup_file])
                    subprocess.run(["./{}".format(setup_file)], shell=True)
                else:
                    print(f"\n❌ {setup_file} not found")
                    print("Please run: chmod +x setup.sh && ./setup.sh")
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(0)

if __name__ == "__main__":
    main()
