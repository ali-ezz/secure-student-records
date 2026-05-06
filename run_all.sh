#!/bin/bash
# ========================================
# 🚀 SRMS - Master Launcher
# Starts EVERYTHING with one command!
# ========================================

set -e  # Exit on error

PROJECT_DIR="/home/Ahmed-abobakr/Downloads/DS_ahmed"
cd "$PROJECT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=========================================="
echo "  🔐 SRMS - Master Launcher"
echo "  Starting All Components..."
echo "=========================================="
echo -e "${NC}"

# ========================================
# 1. Start Docker (SQL Server)
# ========================================
echo -e "${GREEN}[1/5] Starting SQL Server (Docker)...${NC}"

if ! docker ps | grep -q sqlserver2022; then
    if docker ps -a | grep -q sqlserver2022; then
        echo "  → SQL Server container exists, starting..."
        docker start sqlserver2022 > /dev/null 2>&1
    else
        echo "  → SQL Server container not found, creating..."
        docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Srms@2024!" \
            -p 1433:1433 --name sqlserver2022 --hostname sqlserver \
            -d mcr.microsoft.com/mssql/server:2022-latest > /dev/null 2>&1
    fi
    
    echo "  → Waiting for SQL Server to be ready..."
    sleep 10
else
    echo "  ✓ SQL Server already running"
fi

# Test connection
if docker exec sqlserver2022 /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P 'Srms@2024!' -C -Q "SELECT 1" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ SQL Server is ready!${NC}"
else
    echo -e "  ${YELLOW}⚠ SQL Server connection test failed, but continuing...${NC}"
fi

echo ""

# ========================================
# 2. Start DBeaver (Optional)
# ========================================
echo -e "${GREEN}[2/5] Starting DBeaver...${NC}"

SQL_FILES=(
    "$PROJECT_DIR/sql/sqlserver_schema.sql"
    "$PROJECT_DIR/sql/sqlserver_roles.sql"
    "$PROJECT_DIR/sql/sqlserver_views.sql"
    "$PROJECT_DIR/sql/sqlserver_procedures_fixed.sql"
    "$PROJECT_DIR/sql/sqlserver_sample_data.sql"
)

if command -v dbeaver &> /dev/null || command -v dbeaver-ce &> /dev/null; then
    DBEAVER_CMD="dbeaver"
    command -v dbeaver &> /dev/null || DBEAVER_CMD="dbeaver-ce"
    
    echo "  → Opening DBeaver with SQL files..."
    $DBEAVER_CMD "${SQL_FILES[@]}" &> /dev/null &
    echo -e "  ${GREEN}✓ DBeaver launched!${NC}"
else
    echo -e "  ${YELLOW}⚠ DBeaver not found (optional, skipping)${NC}"
    echo "    Install: sudo snap install dbeaver-ce"
fi

echo ""

# ========================================
# 3. Start Web Database Viewer (Flask)
# ========================================
echo -e "${GREEN}[3/5] Starting Web Database Viewer...${NC}"

if [ -f "$PROJECT_DIR/db_viewer.py" ]; then
    # Activate venv and start Flask
    source .venv/bin/activate
    
    echo "  → Starting Flask server on http://localhost:5000..."
    python db_viewer.py &> /tmp/srms_web_viewer.log &
    FLASK_PID=$!
    
    # Wait a moment for Flask to start
    sleep 2
    
    if ps -p $FLASK_PID > /dev/null; then
        echo -e "  ${GREEN}✓ Web Viewer running at http://localhost:5000${NC}"
        echo "    PID: $FLASK_PID"
    else
        echo -e "  ${YELLOW}⚠ Web Viewer failed to start${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ db_viewer.py not found (skipping)${NC}"
fi

echo ""

# ========================================
# 4. Open Web Browser (Optional)
# ========================================
echo -e "${GREEN}[4/5] Opening Web Browser...${NC}"

if command -v xdg-open &> /dev/null; then
    sleep 1
    xdg-open http://localhost:5000 &> /dev/null &
    echo -e "  ${GREEN}✓ Browser opened!${NC}"
else
    echo "  → Manually open: http://localhost:5000"
fi

echo ""

# ========================================
# 5. Start GUI Application (Main)
# ========================================
echo -e "${GREEN}[5/5] Starting SRMS GUI Application...${NC}"

source .venv/bin/activate
echo "  → Launching main application..."
echo ""

echo -e "${BLUE}"
echo "=========================================="
echo "  ✅ All Components Started!"
echo "=========================================="
echo ""
echo "Running Services:"
echo "  🐳 SQL Server   : localhost:1433"
echo "  🌐 Web Viewer   : http://localhost:5000"
echo "  💾 DBeaver      : Opened (if installed)"
echo "  🖥️  GUI App      : Starting now..."
echo ""
echo "Press Ctrl+C in GUI to stop all services"
echo "=========================================="
echo -e "${NC}"
echo ""

# Run GUI (foreground - blocks until closed)
python src/gui/main.py

# ========================================
# Cleanup when GUI closes
# ========================================
echo ""
echo -e "${YELLOW}GUI closed. Cleaning up...${NC}"

# Kill Flask if running
if [ ! -z "$FLASK_PID" ]; then
    if ps -p $FLASK_PID > /dev/null 2>&1; then
        kill $FLASK_PID 2>/dev/null
        echo "  ✓ Web Viewer stopped"
    fi
fi

# Optionally stop Docker
read -p "Stop SQL Server container? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker stop sqlserver2022 > /dev/null 2>&1
    echo "  ✓ SQL Server stopped"
else
    echo "  → SQL Server still running (run: docker stop sqlserver2022)"
fi

echo ""
echo -e "${GREEN}✓ SRMS Launcher finished!${NC}"
