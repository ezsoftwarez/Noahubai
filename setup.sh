#!/bin/bash
# Noahubai Installation Script for Linux/macOS
# This script handles the installation of Noahubai on Unix-like systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}"
    cat << "EOF"
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
EOF
    echo -e "${NC}"
}

check_python() {
    echo -e "\n${BLUE}Checking Python installation...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed${NC}"
        echo -e "${YELLOW}   Please install Python 3.10+ first:${NC}"
        echo -e "${YELLOW}   Ubuntu/Debian: sudo apt-get install python3 python3-venv python3-pip${NC}"
        echo -e "${YELLOW}   macOS: brew install python3${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅ Python found: $PYTHON_VERSION${NC}"
}

select_install_dir() {
    echo -e "\n${BLUE}📁 Installation Directory Selection${NC}"
    
    DEFAULT_INSTALL_DIR="$HOME/.local/share/noahubai"
    
    echo -e "Default installation path:\n   $DEFAULT_INSTALL_DIR"
    
    read -p "Use default path? (Y/n): " -r response
    
    if [[ "$response" =~ ^[Nn]$ ]]; then
        read -p "Enter custom installation path: " INSTALL_DIR
    else
        INSTALL_DIR="$DEFAULT_INSTALL_DIR"
    fi
    
    mkdir -p "$INSTALL_DIR"
    echo -e "${GREEN}✅ Installation directory: $INSTALL_DIR${NC}"
}

create_venv() {
    echo -e "\n${BLUE}🔧 Creating Virtual Environment${NC}"
    
    VENV_DIR="$INSTALL_DIR/venv"
    
    if [ -d "$VENV_DIR" ]; then
        echo -e "${YELLOW}Virtual environment already exists, skipping...${NC}"
    else
        python3 -m venv "$VENV_DIR"
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    fi
    
    source "$VENV_DIR/bin/activate"
}

install_dependencies() {
    echo -e "\n${BLUE}📦 Installing Dependencies${NC}"
    
    pip install --upgrade pip -q
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        pip install -r "$SCRIPT_DIR/requirements.txt" -q
        echo -e "${GREEN}✅ Dependencies installed from requirements.txt${NC}"
    else
        echo -e "${YELLOW}⚠️  requirements.txt not found, installing core dependencies...${NC}"
        pip install fastapi uvicorn pydantic python-multipart -q
        echo -e "${GREEN}✅ Core dependencies installed${NC}"
    fi
}

copy_files() {
    echo -e "\n${BLUE}📋 Copying Application Files${NC}"
    
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    for dir in core agents backend; do
        if [ -d "$SCRIPT_DIR/$dir" ]; then
            cp -r "$SCRIPT_DIR/$dir" "$INSTALL_DIR/"
            echo -e "  ${GREEN}✓${NC} Copied $dir/"
        fi
    done
    
    if [ -f "$SCRIPT_DIR/main.py" ]; then
        cp "$SCRIPT_DIR/main.py" "$INSTALL_DIR/"
        echo -e "  ${GREEN}✓${NC} Copied main.py"
    fi
    
    echo -e "${GREEN}✅ Application files copied${NC}"
}

create_shortcuts() {
    echo -e "\n${BLUE}🔗 Creating Shortcuts${NC}"
    
    # Create run script
    PYTHON_EXE="$INSTALL_DIR/venv/bin/python"
    MAIN_PY="$INSTALL_DIR/main.py"
    
    RUN_SCRIPT="$INSTALL_DIR/run_noahubai.sh"
    cat > "$RUN_SCRIPT" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
source venv/bin/activate
python main.py \"\$@\"
EOF
    
    chmod +x "$RUN_SCRIPT"
    echo -e "  ${GREEN}✓${NC} Created run_noahubai.sh"
    
    # Create desktop entry for Linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        DESKTOP_DIR="$HOME/.local/share/applications"
        mkdir -p "$DESKTOP_DIR"
        
        DESKTOP_FILE="$DESKTOP_DIR/noahubai.desktop"
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Noahubai
Comment=Unified AI with Memory, Issues, and Auto-Fixing
Exec=$RUN_SCRIPT
Icon=application-x-python
Terminal=true
Categories=Development;Utility;
EOF
        
        chmod +x "$DESKTOP_FILE"
        echo -e "  ${GREEN}✓${NC} Created desktop entry"
    fi
    
    echo -e "${GREEN}✅ Shortcuts created${NC}"
}

create_config() {
    echo -e "\n${BLUE}⚙️  Creating Configuration Files${NC}"
    
    ENV_FILE="$INSTALL_DIR/.env"
    cat > "$ENV_FILE" << EOF
# Noahubai Configuration
# Generated: $(date)

HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
AGENT_TIMEOUT=30
MAX_RETRIES=3
EOF
    
    echo -e "  ${GREEN}✓${NC} Created .env file"
    echo -e "${GREEN}✅ Configuration files created${NC}"
}

print_completion() {
    echo -e "\n${GREEN}════════════════════════════════════════════════════════════════════════════════"
    echo "✅ NOAHUBAI INSTALLATION COMPLETED SUCCESSFULLY!"
    echo -e "════════════════════════════════════════════════════════════════════════════════${NC}"
    
    echo -e "\n${BLUE}📁 Installation Directory:${NC} $INSTALL_DIR"
    
    echo -e "\n${BLUE}🚀 Quick Start:${NC}"
    echo -e "   1. Run: $INSTALL_DIR/run_noahubai.sh"
    echo -e "   2. Open browser: http://localhost:8000"
    echo -e "   3. Check the dashboard for agent status"
    
    echo -e "\n${BLUE}📖 Documentation:${NC}"
    echo -e "   API Docs: http://localhost:8000/docs"
    
    echo -e "\n${GREEN}════════════════════════════════════════════════════════════════════════════════${NC}\n"
}

# Main installation flow
main() {
    print_header
    
    check_python
    select_install_dir
    create_venv
    install_dependencies
    copy_files
    create_shortcuts
    create_config
    print_completion
    
    read -p "Start Noahubai now? (Y/n): " -r response
    
    if ! [[ "$response" =~ ^[Nn]$ ]]; then
        echo -e "\n${BLUE}🚀 Starting Noahubai...${NC}\n"
        "$INSTALL_DIR/run_noahubai.sh"
    fi
}

# Run main function
main
