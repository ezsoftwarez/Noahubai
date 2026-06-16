"""
Noahubai Setup Script
Installs Noahubai system with all dependencies and creates shortcuts
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
from datetime import datetime


class NoahubaiSetup:
    """Setup wizard for Noahubai installation"""
    
    def __init__(self):
        self.install_dir = None
        self.venv_dir = None
        self.python_exe = sys.executable
    
    def print_header(self):
        """Print installation header"""
        header = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                   🤖 NOAHUBAI INSTALLATION WIZARD 🤖                         ║
║                                                                              ║
║          Unified AI with Memory, Issues, and Auto-Fixing                    ║
║                                                                              ║
║  • Continuous Learning & Memory Management                                  ║
║  • Intelligent Issue Detection & Tracking                                   ║
║  • Automated Problem Resolution                                             ║
║  • Multi-Agent Architecture (Fully Detached)                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(header)
    
    def select_installation_path(self):
        """Let user select installation directory"""
        print("\n📁 Installation Directory Selection")
        print("=" * 50)
        
        if sys.platform == "win32":
            default_path = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))) / "Noahubai"
        else:
            default_path = Path.home() / ".local" / "share" / "noahubai"
        
        print(f"\nDefault installation path:")
        print(f"  {default_path}")
        
        response = input("\nUse default path? (Y/n): ").strip().lower()
        
        if response == 'n':
            custom_path = input("Enter custom installation path: ").strip()
            self.install_dir = Path(custom_path)
        else:
            self.install_dir = default_path
        
        # Create directory if it doesn't exist
        self.install_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n✅ Installation directory: {self.install_dir}")
    
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        print("\n🔧 Creating Virtual Environment")
        print("=" * 50)
        
        self.venv_dir = self.install_dir / "venv"
        
        try:
            print(f"Creating venv at: {self.venv_dir}")
            subprocess.check_call([self.python_exe, "-m", "venv", str(self.venv_dir)])
            print("✅ Virtual environment created successfully")
        except Exception as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
        
        return True
    
    def get_venv_python(self):
        """Get Python executable from venv"""
        if sys.platform == "win32":
            return self.venv_dir / "Scripts" / "python.exe"
        else:
            return self.venv_dir / "bin" / "python"
    
    def get_venv_pip(self):
        """Get pip executable from venv"""
        if sys.platform == "win32":
            return self.venv_dir / "Scripts" / "pip.exe"
        else:
            return self.venv_dir / "bin" / "pip"
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("\n📦 Installing Dependencies")
        print("=" * 50)
        
        pip_exe = self.get_venv_pip()
        requirements_file = Path(__file__).parent / "requirements.txt"
        
        if not requirements_file.exists():
            print(f"⚠️  requirements.txt not found at {requirements_file}")
            print("Skipping dependency installation")
            return True
        
        try:
            print(f"Installing from {requirements_file}...")
            subprocess.check_call([
                str(pip_exe),
                "install",
                "-r",
                str(requirements_file),
                "-q"
            ])
            print("✅ Dependencies installed successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def copy_application_files(self):
        """Copy application files to installation directory"""
        print("\n📋 Copying Application Files")
        print("=" * 50)
        
        source_dir = Path(__file__).parent
        
        # Directories to copy
        dirs_to_copy = ["core", "agents", "backend", "frontend", "config", "tests", "docs"]
        files_to_copy = ["main.py", "requirements.txt", "README.md", "setup.py"]
        
        try:
            for dir_name in dirs_to_copy:
                src = source_dir / dir_name
                dst = self.install_dir / dir_name
                
                if src.exists():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    print(f"  ✓ Copied {dir_name}/")
            
            for file_name in files_to_copy:
                src = source_dir / file_name
                dst = self.install_dir / file_name
                
                if src.exists():
                    shutil.copy2(src, dst)
                    print(f"  ✓ Copied {file_name}")
            
            print("\n✅ Application files copied successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to copy files: {e}")
            return False
    
    def create_shortcuts(self):
        """Create desktop/menu shortcuts"""
        print("\n🔗 Creating Shortcuts")
        print("=" * 50)
        
        try:
            if sys.platform == "win32":
                self.create_windows_shortcuts()
            else:
                self.create_linux_shortcuts()
            
            print("✅ Shortcuts created successfully")
            return True
        except Exception as e:
            print(f"⚠️  Failed to create shortcuts: {e}")
            # Don't fail installation if shortcuts fail
            return True
    
    def create_windows_shortcuts(self):
        """Create Windows shortcuts"""
        import winreg
        
        venv_python = self.get_venv_python()
        main_py = self.install_dir / "main.py"
        
        # Create desktop shortcut
        desktop_path = Path.home() / "Desktop" / "Noahubai.lnk"
        
        # Create batch file to run application
        batch_file = self.install_dir / "run_noahubai.bat"
        batch_content = f"""@echo off
"{venv_python}" "{main_py}" %*
pause
"""
        
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        print(f"  ✓ Created run_noahubai.bat")
        
        # Create start menu shortcut batch
        start_menu_batch = self.install_dir / "create_shortcuts.bat"
        start_menu_content = f"""@echo off
setlocal

set SCRIPT_DIR=%~dp0
set PYTHON_EXE={venv_python}
set MAIN_PY={main_py}

REM Create shortcut (requires PowerShell)
powershell -NoProfile -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Noahubai.lnk'); $Shortcut.TargetPath = '%PYTHON_EXE%'; $Shortcut.Arguments = '%MAIN_PY%'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.IconLocation = '%SCRIPT_DIR%'; $Shortcut.Save()"

echo Shortcuts created successfully!
pause
"""
        
        with open(start_menu_batch, 'w') as f:
            f.write(start_menu_content)
        
        print(f"  ✓ Created create_shortcuts.bat")
    
    def create_linux_shortcuts(self):
        """Create Linux desktop shortcuts"""
        venv_python = self.get_venv_python()
        main_py = self.install_dir / "main.py"
        
        # Create desktop entry
        desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Noahubai
Comment=Unified AI with Memory, Issues, and Auto-Fixing
Exec={venv_python} {main_py}
Icon=application-x-python
Terminal=true
Categories=Development;Utility;
"""
        
        desktop_file = Path.home() / ".local" / "share" / "applications" / "noahubai.desktop"
        desktop_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(desktop_file, 'w') as f:
            f.write(desktop_entry)
        
        os.chmod(desktop_file, 0o755)
        print(f"  ✓ Created desktop entry")
        
        # Create shell script
        shell_script = self.install_dir / "run_noahubai.sh"
        shell_content = f"""#!/bin/bash
{venv_python} {main_py} "$@"
"""
        
        with open(shell_script, 'w') as f:
            f.write(shell_content)
        
        os.chmod(shell_script, 0o755)
        print(f"  ✓ Created run_noahubai.sh")
    
    def create_config_files(self):
        """Create configuration files"""
        print("\n⚙️  Creating Configuration Files")
        print("=" * 50)
        
        # Create .env file
        env_file = self.install_dir / ".env"
        env_content = f"""# Noahubai Configuration
# Generated: {datetime.now().isoformat()}

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=noahubai.log

# Agents
AGENT_TIMEOUT=30
MAX_RETRIES=3

# Memory
MEMORY_MAX_SIZE=10000
MEMORY_CLEANUP_INTERVAL=3600
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"  ✓ Created .env configuration file")
        
        # Create installation info
        install_info = {
            "version": "1.0.0",
            "installed_at": datetime.now().isoformat(),
            "install_dir": str(self.install_dir),
            "venv_dir": str(self.venv_dir),
            "python_version": sys.version,
            "platform": sys.platform
        }
        
        info_file = self.install_dir / "install_info.json"
        with open(info_file, 'w') as f:
            json.dump(install_info, f, indent=2)
        
        print(f"  ✓ Created install_info.json")
        print("\n✅ Configuration files created successfully")
    
    def print_completion_summary(self):
        """Print installation completion summary"""
        print("\n" + "=" * 80)
        print("✅ NOAHUBAI INSTALLATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        print(f"\n📁 Installation Directory: {self.install_dir}")
        print(f"🐍 Virtual Environment: {self.venv_dir}")
        
        print("\n🚀 Quick Start:")
        
        if sys.platform == "win32":
            print(f"   1. Open Command Prompt")
            print(f"   2. Run: {self.install_dir}\\run_noahubai.bat")
            print(f"   3. Open browser: http://localhost:8000")
        else:
            print(f"   1. Open Terminal")
            print(f"   2. Run: {self.install_dir}/run_noahubai.sh")
            print(f"   3. Open browser: http://localhost:8000")
        
        print("\n📚 Documentation:")
        print(f"   - README: {self.install_dir / 'README.md'}")
        print(f"   - API Docs: http://localhost:8000/docs")
        
        print("\n🔧 Configuration:")
        print(f"   - Edit settings: {self.install_dir / '.env'}")
        print(f"   - Install info: {self.install_dir / 'install_info.json'}")
        
        print("\n📖 Next Steps:")
        print("   1. Start the application")
        print("   2. Open http://localhost:8000 in your browser")
        print("   3. Check the dashboard for agent status")
        print("   4. Begin using the system (learn patterns, detect issues, fix problems)")
        
        print("\n💡 Features:")
        print("   ✓ Memory Agent - Learn patterns and store solutions")
        print("   ✓ Issue Agent - Detect and track issues")
        print("   ✓ Fixer Agent - Automatically fix problems")
        print("   ✓ Real-time WebSocket updates")
        print("   ✓ Comprehensive REST API")
        print("   ✓ Advanced settings and configuration")
        
        print("\n⚙️  System Information:")
        print(f"   Python: {sys.version.split()[0]}")
        print(f"   Platform: {sys.platform}")
        print(f"   Architecture: {os.name}")
        
        print("\n" + "=" * 80)
        print("Thank you for installing Noahubai! 🎉")
        print("For support, visit: https://github.com/ezsoftwarez/Noahubai")
        print("=" * 80 + "\n")
    
    def run(self):
        """Run the installation wizard"""
        try:
            self.print_header()
            
            # Step 1: Select installation path
            self.select_installation_path()
            
            # Step 2: Create virtual environment
            if not self.create_virtual_environment():
                return False
            
            # Step 3: Install dependencies
            if not self.install_dependencies():
                print("⚠️  Continuing despite dependency installation issues...")
            
            # Step 4: Copy application files
            if not self.copy_application_files():
                return False
            
            # Step 5: Create configuration files
            self.create_config_files()
            
            # Step 6: Create shortcuts
            self.create_shortcuts()
            
            # Step 7: Print completion summary
            self.print_completion_summary()
            
            return True
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Installation cancelled by user")
            return False
        except Exception as e:
            print(f"\n\n❌ Installation failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    setup = NoahubaiSetup()
    success = setup.run()
    
    if not success:
        sys.exit(1)
    
    # Ask if user wants to start the application
    print("\nWould you like to start Noahubai now? (Y/n): ", end="")
    response = input().strip().lower()
    
    if response != 'n':
        import subprocess
        venv_python = setup.get_venv_python()
        main_py = setup.install_dir / "main.py"
        
        print("\n🚀 Starting Noahubai...\n")
        try:
            subprocess.run([str(venv_python), str(main_py)])
        except Exception as e:
            print(f"Failed to start application: {e}")


if __name__ == "__main__":
    main()
