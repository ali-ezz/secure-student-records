#!/bin/bash
# 🚀 SRMS Project Launcher
# Opens DBeaver with SQL files and runs the GUI application

PROJECT_DIR="/home/Ahmed-abobakr/Downloads/DS_ahmed"
cd "$PROJECT_DIR"

echo "=================================================="
echo "  🔐 SRMS - Secure Student Records"
echo "  Starting Database Tools + GUI Application"
echo "=================================================="
echo ""

# SQL Files to open in DBeaver
SQL_FILES=(
    "$PROJECT_DIR/sql/sqlserver_schema.sql"
    "$PROJECT_DIR/sql/sqlserver_roles.sql"
    "$PROJECT_DIR/sql/sqlserver_views.sql"
    "$PROJECT_DIR/sql/sqlserver_procedures.sql"
    "$PROJECT_DIR/sql/sqlserver_sample_data.sql"
)

# Check if DBeaver is installed
if command -v dbeaver &> /dev/null || command -v dbeaver-ce &> /dev/null; then
    echo "✓ Opening DBeaver with SQL files..."
    
    # Try both possible dbeaver commands
    if command -v dbeaver &> /dev/null; then
        DBEAVER_CMD="dbeaver"
    else
        DBEAVER_CMD="dbeaver-ce"
    fi
    
    # Open DBeaver with all SQL files in background
    $DBEAVER_CMD "${SQL_FILES[@]}" &> /dev/null &
    
    echo "  → Opened ${#SQL_FILES[@]} SQL files"
    sleep 2
else
    echo "⚠️  DBeaver not found. Skipping SQL files."
    echo "   Install: sudo snap install dbeaver-ce"
    echo ""
fi

# Activate virtual environment and run GUI
echo "✓ Starting SRMS GUI Application..."
echo ""

source .venv/bin/activate
python src/gui/main.py

echo ""
echo "✓ Application closed."
