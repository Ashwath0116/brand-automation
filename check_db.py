import sqlite3

conn = sqlite3.connect("backend/bizforge.db")
c = conn.cursor()

with open("db_report.md", "w", encoding="utf-8") as f:
    f.write("# BizForge Database Report\n\n")

    # Tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()
    f.write("## Tables\n")
    for t in tables:
        c.execute(f"SELECT COUNT(*) FROM [{t[0]}]")
        count = c.fetchone()[0]
        f.write(f"- **{t[0]}** - {count} rows\n")

    # Users
    f.write("\n## Users\n\n")
    f.write("| ID | Name | Email | Provider | Admin | Created | Last Login |\n")
    f.write("|---|---|---|---|---|---|---|\n")
    c.execute("SELECT id, name, email, provider, is_admin, created_at, last_login FROM users")
    users = c.fetchall()
    for u in users:
        f.write(f"| {u[0]} | {u[1]} | {u[2]} | {u[3]} | {'Yes' if u[4] else 'No'} | {u[5]} | {u[6]} |\n")
    f.write(f"\n**Total users: {len(users)}**\n")

    # Sessions
    f.write("\n## Active Sessions\n\n")
    c.execute("SELECT id, user_id, substr(token, 1, 15), created_at FROM sessions")
    sessions = c.fetchall()
    f.write(f"**Total active sessions: {len(sessions)}**\n\n")
    for s in sessions:
        f.write(f"- Session [{s[0]}] User ID: {s[1]} | Token: {s[2]}... | {s[3]}\n")

    # Activity Logs
    f.write("\n## Activity Logs (Recent 20)\n\n")
    c.execute("""
        SELECT id, user_email, action, status, ip_address, created_at,
               request_data, response_data
        FROM activity_logs ORDER BY id DESC LIMIT 20
    """)
    logs = c.fetchall()

    if logs:
        for l in logs:
            f.write(f"### Log #{l[0]}\n")
            f.write(f"- **User:** {l[1] or 'Anonymous'}\n")
            f.write(f"- **Action:** {l[2]}\n")
            f.write(f"- **Status:** {l[3]}\n")
            f.write(f"- **IP:** {l[4]}\n")
            f.write(f"- **Time:** {l[5]}\n")
            f.write(f"- **Input:**\n```json\n{l[6]}\n```\n")
            f.write(f"- **Output:**\n```json\n{l[7]}\n```\n\n")
    else:
        f.write("No activity logs yet.\n")

    c.execute("SELECT COUNT(*) FROM activity_logs")
    f.write(f"\n**Total activity logs: {c.fetchone()[0]}**\n")

conn.close()
print("Report written to db_report.md")
