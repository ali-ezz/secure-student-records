"""
SRMS Web Database Viewer
Browse SQL Server database via web browser
Access: http://localhost:5000
"""

from flask import Flask, render_template_string, request
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database.connection import get_database, is_sqlserver

app = Flask(__name__)

def get_base_template(title, page, content):
    """Generate complete HTML page."""
    is_sql = is_sqlserver()
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔐 SRMS - {title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        :root {{
            --bg-primary: #000000;
            --bg-secondary: #0a0a0a;
            --bg-card: #1a1a1a;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent: #3b82f6;
            --success: #22c55e;
            --error: #ef4444;
            --border: #2a2a2a;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: var(--text-primary);
            min-height: 100vh;
        }}
        
        .header {{
            background: var(--bg-secondary);
            padding: 20px 40px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{
            font-size: 24px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .header h1 span {{ color: var(--accent); }}
        
        .status {{
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--success);
        }}
        
        .status-dot {{
            width: 10px;
            height: 10px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .container {{
            display: flex;
            min-height: calc(100vh - 80px);
        }}
        
        .sidebar {{
            width: 250px;
            background: var(--bg-secondary);
            padding: 20px;
            border-right: 1px solid var(--border);
        }}
        
        .sidebar h3 {{
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 15px;
        }}
        
        .sidebar a {{
            display: block;
            padding: 12px 15px;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: 8px;
            margin-bottom: 5px;
            transition: all 0.2s;
        }}
        
        .sidebar a:hover {{
            background: var(--accent);
            color: white;
        }}
        
        .sidebar a.active {{
            background: var(--accent);
            color: white;
        }}
        
        .main {{
            flex: 1;
            padding: 30px;
        }}
        
        .card {{
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border);
            margin-bottom: 20px;
            overflow: hidden;
        }}
        
        .card-header {{
            padding: 15px 20px;
            border-bottom: 1px solid var(--border);
            font-weight: 600;
        }}
        
        .card-body {{
            padding: 20px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background: var(--bg-secondary);
            color: var(--accent);
            font-weight: 600;
        }}
        
        tr:hover {{ background: rgba(59, 130, 246, 0.1); }}
        
        .query-box {{
            width: 100%;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 15px;
            color: var(--text-primary);
            font-family: 'Consolas', monospace;
            font-size: 14px;
            resize: vertical;
            min-height: 100px;
        }}
        
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-block;
        }}
        
        .btn-primary {{
            background: var(--accent);
            color: white;
        }}
        
        .btn-primary:hover {{ background: #2563eb; }}
        
        .btn-sm {{
            padding: 6px 12px;
            font-size: 12px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        
        .stat-card .number {{
            font-size: 32px;
            font-weight: bold;
            color: var(--accent);
        }}
        
        .stat-card .label {{
            color: var(--text-secondary);
            margin-top: 5px;
        }}
        
        pre {{
            background: var(--bg-secondary);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Consolas', monospace;
            white-space: pre-wrap;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .badge-success {{ background: rgba(34, 197, 94, 0.2); color: var(--success); }}
        .badge-info {{ background: rgba(59, 130, 246, 0.2); color: var(--accent); }}
        
        h2 {{ margin-bottom: 20px; }}
        
        .error {{ color: var(--error); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔐 <span>SRMS</span> Database Viewer</h1>
        <div class="status">
            <div class="status-dot"></div>
            {'SQL Server Connected' if is_sql else 'SQLite Mode'}
        </div>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <h3>📋 Navigation</h3>
            <a href="/" class="{'active' if page == 'home' else ''}">📊 Overview</a>
            <a href="/tables" class="{'active' if page == 'tables' else ''}">📁 Tables</a>
            <a href="/users" class="{'active' if page == 'users' else ''}">👥 Users</a>
            <a href="/students" class="{'active' if page == 'students' else ''}">🎓 Students</a>
            <a href="/courses" class="{'active' if page == 'courses' else ''}">📚 Courses</a>
            <a href="/grades" class="{'active' if page == 'grades' else ''}">📈 Grades</a>
            <a href="/procedures" class="{'active' if page == 'procedures' else ''}">⚙️ Procedures</a>
            <a href="/query" class="{'active' if page == 'query' else ''}">💻 SQL Query</a>
            
            <h3 style="margin-top: 30px;">🔒 Security</h3>
            <a href="/roles" class="{'active' if page == 'roles' else ''}">👤 RBAC Roles</a>
            <a href="/views" class="{'active' if page == 'views' else ''}">👁️ MLS Views</a>
            <a href="/audit" class="{'active' if page == 'audit' else ''}">📜 Audit Log</a>
        </div>
        
        <div class="main">
            {content}
        </div>
    </div>
</body>
</html>
'''

def get_db():
    return get_database()

@app.route('/')
def home():
    db = get_db()
    stats = {'Users': 0, 'Students': 0, 'Instructors': 0, 'Courses': 0, 'Grades': 0}
    try:
        stats = {
            'Users': db.fetch_one("SELECT COUNT(*) as c FROM USERS")['c'],
            'Students': db.fetch_one("SELECT COUNT(*) as c FROM STUDENT")['c'],
            'Instructors': db.fetch_one("SELECT COUNT(*) as c FROM INSTRUCTOR")['c'],
            'Courses': db.fetch_one("SELECT COUNT(*) as c FROM COURSE")['c'],
            'Grades': db.fetch_one("SELECT COUNT(*) as c FROM GRADES")['c'],
        }
    except: pass
    
    stats_html = ''.join([f'''
        <div class="stat-card">
            <div class="number">{count}</div>
            <div class="label">{name}</div>
        </div>
    ''' for name, count in stats.items()])
    
    content = f'''
    <h2>📊 Database Overview</h2>
    
    <div class="stats-grid">{stats_html}</div>
    
    <div class="card">
        <div class="card-header">🔗 Connection Info</div>
        <div class="card-body">
            <table>
                <tr><th>Server</th><td>localhost:1433</td></tr>
                <tr><th>Database</th><td>SRMS_SecureDB</td></tr>
                <tr><th>Type</th><td>Microsoft SQL Server 2022</td></tr>
                <tr><th>Status</th><td><span class="badge badge-success">Connected</span></td></tr>
            </table>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header">🛡️ Security Models</div>
        <div class="card-body">
            <table>
                <tr><th>Model</th><th>Status</th><th>Description</th></tr>
                <tr><td>RBAC</td><td><span class="badge badge-success">Active</span></td><td>5 roles with permissions</td></tr>
                <tr><td>MLS</td><td><span class="badge badge-success">Active</span></td><td>Bell-LaPadula enforcement</td></tr>
                <tr><td>Encryption</td><td><span class="badge badge-success">Active</span></td><td>AES-256 symmetric key</td></tr>
                <tr><td>Inference Control</td><td><span class="badge badge-success">Active</span></td><td>Min 3 records for stats</td></tr>
                <tr><td>Flow Control</td><td><span class="badge badge-success">Active</span></td><td>Prevent data downflow</td></tr>
            </table>
        </div>
    </div>
    '''
    
    return get_base_template('Overview', 'home', content)

@app.route('/tables')
def tables():
    db = get_db()
    tables = []
    try:
        tables = db.fetch_all("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
    except: pass
    
    rows = ''.join([f'''
        <tr>
            <td>{i}</td>
            <td>{t['TABLE_NAME']}</td>
            <td><a href="/table/{t['TABLE_NAME']}" class="btn btn-primary btn-sm">View Data</a></td>
        </tr>
    ''' for i, t in enumerate(tables, 1)])
    
    content = f'''
    <h2>📁 Database Tables</h2>
    <div class="card">
        <div class="card-body">
            <table>
                <tr><th>#</th><th>Table Name</th><th>Action</th></tr>
                {rows}
            </table>
        </div>
    </div>
    '''
    
    return get_base_template('Tables', 'tables', content)

@app.route('/table/<name>')
def view_table(name):
    db = get_db()
    data = []
    try:
        data = db.fetch_all(f"SELECT TOP 100 * FROM [{name}]")
    except Exception as e:
        return get_base_template('Error', 'tables', f'<h2>Error</h2><p class="error">{e}</p>')
    
    if not data:
        return get_base_template(name, 'tables', f'<h2>Table: {name}</h2><p>No data</p>')
    
    columns = list(data[0].keys())
    headers = ''.join([f'<th>{c}</th>' for c in columns])
    rows = ''.join([
        '<tr>' + ''.join([f'<td>{str(row.get(c, ""))[:50]}</td>' for c in columns]) + '</tr>'
        for row in data
    ])
    
    content = f'''
    <h2>📋 Table: {name}</h2>
    <div class="card">
        <div class="card-body" style="overflow-x: auto;">
            <table>
                <tr>{headers}</tr>
                {rows}
            </table>
        </div>
    </div>
    <a href="/tables" class="btn btn-primary" style="margin-top: 20px;">← Back to Tables</a>
    '''
    
    return get_base_template(name, 'tables', content)

@app.route('/users')
def users():
    db = get_db()
    data = []
    try:
        data = db.fetch_all("SELECT UserID, Username, Role, ClearanceLevel, IsActive FROM USERS")
    except: pass
    
    rows = ''.join([f'''
        <tr>
            <td>{u['UserID']}</td>
            <td>{u['Username']}</td>
            <td><span class="badge badge-info">{u['Role']}</span></td>
            <td>{u['ClearanceLevel']}</td>
            <td>{'✅' if u.get('IsActive', 1) else '❌'}</td>
        </tr>
    ''' for u in data])
    
    content = f'''
    <h2>👥 Users</h2>
    <div class="card">
        <div class="card-body">
            <table>
                <tr><th>ID</th><th>Username</th><th>Role</th><th>Clearance</th><th>Active</th></tr>
                {rows}
            </table>
        </div>
    </div>
    '''
    
    return get_base_template('Users', 'users', content)

@app.route('/students')
def students():
    db = get_db()
    data = []
    try:
        data = db.fetch_all("SELECT StudentID, FullName, Email, Department, Status FROM STUDENT")
    except: pass
    
    rows = ''.join([f'''
        <tr>
            <td>{s['StudentID']}</td>
            <td>{s['FullName']}</td>
            <td>{s['Email']}</td>
            <td>{s.get('Department', '')}</td>
            <td>{s.get('Status', '')}</td>
        </tr>
    ''' for s in data])
    
    content = f'''
    <h2>🎓 Students</h2>
    <div class="card">
        <div class="card-body">
            <table>
                <tr><th>ID</th><th>Name</th><th>Email</th><th>Department</th><th>Status</th></tr>
                {rows}
            </table>
        </div>
    </div>
    '''
    
    return get_base_template('Students', 'students', content)

@app.route('/courses')
def courses():
    db = get_db()
    data = []
    try:
        data = db.fetch_all("SELECT CourseID, CourseCode, CourseName, Credits, Department FROM COURSE")
    except: pass
    
    rows = ''.join([f'''
        <tr>
            <td>{c['CourseID']}</td>
            <td>{c['CourseCode']}</td>
            <td>{c['CourseName']}</td>
            <td>{c.get('Credits', 3)}</td>
            <td>{c.get('Department', '')}</td>
        </tr>
    ''' for c in data])
    
    content = f'''
    <h2>📚 Courses</h2>
    <div class="card">
        <div class="card-body">
            <table>
                <tr><th>ID</th><th>Code</th><th>Name</th><th>Credits</th><th>Department</th></tr>
                {rows}
            </table>
        </div>
    </div>
    '''
    
    return get_base_template('Courses', 'courses', content)

@app.route('/grades')
def grades():
    db = get_db()
    data = []
    try:
        data = db.fetch_all("""
            SELECT g.GradeID, s.FullName as Student, c.CourseCode, 
                   g.GradeValue_Display as Grade, g.GradeLetter, g.IsPublished
            FROM GRADES g
            JOIN STUDENT s ON g.StudentID = s.StudentID
            JOIN COURSE c ON g.CourseID = c.CourseID
        """)
    except: pass
    
    rows = ''.join([f'''
        <tr>
            <td>{g['GradeID']}</td>
            <td>{g['Student']}</td>
            <td>{g['CourseCode']}</td>
            <td>{g.get('Grade', '')}</td>
            <td>{g.get('GradeLetter', '')}</td>
            <td>{'✅' if g.get('IsPublished', 0) else '❌'}</td>
        </tr>
    ''' for g in data])
    
    content = f'''
    <h2>📈 Grades</h2>
    <div class="card">
        <div class="card-body">
            <table>
                <tr><th>ID</th><th>Student</th><th>Course</th><th>Grade</th><th>Letter</th><th>Published</th></tr>
                {rows}
            </table>
        </div>
    </div>
    '''
    
    return get_base_template('Grades', 'grades', content)

@app.route('/procedures')
def procedures():
    db = get_db()
    procs = []
    try:
        procs = db.fetch_all("SELECT name FROM sys.procedures ORDER BY name")
    except: pass
    
    rows = ''.join([f'''
        <tr>
            <td>{i}</td>
            <td>{p['name']}</td>
            <td><a href="/procedure/{p['name']}" class="btn btn-primary btn-sm">View Code</a></td>
        </tr>
    ''' for i, p in enumerate(procs, 1)])
    
    content = f'''
    <h2>⚙️ Stored Procedures</h2>
    <div class="card">
        <div class="card-body">
            <table>
                <tr><th>#</th><th>Procedure Name</th><th>Action</th></tr>
                {rows}
            </table>
        </div>
    </div>
    '''
    
    return get_base_template('Procedures', 'procedures', content)

@app.route('/procedure/<name>')
def view_procedure(name):
    db = get_db()
    code = ""
    try:
        result = db.fetch_all(f"EXEC sp_helptext '{name}'")
        code = ''.join([r.get('Text', '') for r in result])
    except Exception as e:
        code = f"Error: {e}"
    
    content = f'''
    <h2>📝 Procedure: {name}</h2>
    <div class="card">
        <div class="card-body">
            <pre>{code}</pre>
        </div>
    </div>
    <a href="/procedures" class="btn btn-primary" style="margin-top: 20px;">← Back to Procedures</a>
    '''
    
    return get_base_template(name, 'procedures', content)

@app.route('/views')
def views():
    db = get_db()
    data = []
    try:
        data = db.fetch_all("SELECT name FROM sys.views ORDER BY name")
    except: pass
    
    rows = ''.join([f'''
        <tr>
            <td>{i}</td>
            <td>{v['name']}</td>
        </tr>
    ''' for i, v in enumerate(data, 1)])
    
    content = f'''
    <h2>👁️ Security Views (MLS)</h2>
    <div class="card">
        <div class="card-body">
            <table>
                <tr><th>#</th><th>View Name</th></tr>
                {rows}
            </table>
        </div>
    </div>
    '''
    
    return get_base_template('Views', 'views', content)

@app.route('/roles')
def roles():
    content = '''
    <h2>👤 RBAC Database Roles</h2>
    <div class="card">
        <div class="card-body">
            <table>
                <tr><th>Role Name</th><th>Clearance</th><th>Permissions</th></tr>
                <tr><td>db_Admin</td><td>4</td><td>Full database access</td></tr>
                <tr><td>db_Instructor</td><td>3</td><td>Manage grades, view students</td></tr>
                <tr><td>db_TA</td><td>2</td><td>Manage attendance</td></tr>
                <tr><td>db_Student</td><td>1</td><td>View own data only</td></tr>
                <tr><td>db_Guest</td><td>0</td><td>Public info only</td></tr>
            </table>
        </div>
    </div>
    '''
    
    return get_base_template('Roles', 'roles', content)

@app.route('/audit')
def audit():
    db = get_db()
    data = []
    try:
        data = db.fetch_all("SELECT TOP 50 * FROM AUDIT_LOG ORDER BY ActionDate DESC")
    except: pass
    
    rows = ''.join([f'''
        <tr>
            <td>{a.get('LogID', '')}</td>
            <td>{a.get('ActionType', '')}</td>
            <td>{a.get('Username', '')}</td>
            <td>{a.get('UserRole', '')}</td>
            <td>{'✅' if a.get('AccessGranted', 0) else '❌'}</td>
            <td>{str(a.get('ActionDate', ''))[:19]}</td>
        </tr>
    ''' for a in data])
    
    content = f'''
    <h2>📜 Audit Log</h2>
    <div class="card">
        <div class="card-body">
            <table>
                <tr><th>ID</th><th>Action</th><th>User</th><th>Role</th><th>Granted</th><th>Time</th></tr>
                {rows}
            </table>
        </div>
    </div>
    '''
    
    return get_base_template('Audit Log', 'audit', content)

@app.route('/query', methods=['GET', 'POST'])
def query():
    result_html = ""
    error = None
    sql = "SELECT * FROM USERS"
    
    if request.method == 'POST':
        sql = request.form.get('sql', '')
        if sql.strip().upper().startswith('SELECT'):
            try:
                db = get_db()
                result = db.fetch_all(sql)
                if result:
                    columns = list(result[0].keys())
                    headers = ''.join([f'<th>{c}</th>' for c in columns])
                    rows = ''.join([
                        '<tr>' + ''.join([f'<td>{str(row.get(c, ""))[:30]}</td>' for c in columns]) + '</tr>'
                        for row in result
                    ])
                    result_html = f'''
                    <div class="card">
                        <div class="card-header">Results ({len(result)} rows)</div>
                        <div class="card-body" style="overflow-x: auto;">
                            <table>
                                <tr>{headers}</tr>
                                {rows}
                            </table>
                        </div>
                    </div>
                    '''
                else:
                    result_html = '<div class="card"><div class="card-body">No results</div></div>'
            except Exception as e:
                error = str(e)
        else:
            error = "Only SELECT queries allowed"
    
    error_html = f'<div class="card" style="border-color: var(--error);"><div class="card-body error">❌ {error}</div></div>' if error else ''
    
    content = f'''
    <h2>💻 SQL Query Console</h2>
    <div class="card">
        <div class="card-header">Enter SQL Query</div>
        <div class="card-body">
            <form method="POST">
                <textarea name="sql" class="query-box">{sql}</textarea>
                <button type="submit" class="btn btn-primary" style="margin-top: 15px;">▶️ Execute</button>
            </form>
        </div>
    </div>
    {error_html}
    {result_html}
    '''
    
    return get_base_template('SQL Query', 'query', content)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🔐 SRMS Web Database Viewer")
    print("  Open in browser: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
