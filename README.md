# 🚀 Placement Tracker MCP

A Python-based placement management tool built using the **Model Context Protocol (MCP)** and SQLite to organize job applications, monitor application progress, and support structured placement reviews.

## ✨ Features

- 📝 **Application Management:** Add and manage job application records.
- 📊 **Application Statistics:** View application counts by status and track reply rates.
- 🔍 **Status Tracking:** Organize applications by stages such as Applied, Online Assessment, Interview, Offer, and Rejected.
- ⏰ **Follow-up Tracking:** Identify applications that have remained in the applied stage for more than seven days.
- 🤖 **Weekly Review:** Use an MCP prompt to review applications, identify pending follow-ups, and plan preparation steps.
- 🗄️ **SQLite Database:** Store application records locally.

## 🛠️ Tech Stack

- **Language:** Python
- **Protocol:** Model Context Protocol (MCP)
- **Database:** SQLite
- **Package Manager:** uv
- **Development Tools:** VS Code, Git, GitHub

## 📁 Project Structure

```text
placement-tracker/
├── src/
│   └── placement_tracker/
├── server.py
├── client.py
├── applications.db
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
└── README.md
```

The local database and environment files are excluded from version control.

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.12 or a compatible version supported by the project
- uv package manager
- Node.js and npm (required for the MCP Inspector development workflow)

### 1. Clone the repository

```bash
git clone https://github.com/AISHAANAND/placement-tracker-mcp.git
cd placement-tracker-mcp
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Run the MCP development server

```bash
uv run mcp dev server.py
```

This starts the MCP Inspector development workflow so you can test the server's available tools and prompts.

## 🔄 How It Works

1. The MCP server exposes placement-management tools.
2. Application records are stored in a local SQLite database.
3. Statistics summarize applications and their current statuses.
4. Stale-application checks help identify potential follow-ups.
5. The weekly review prompt helps organize next steps and placement preparation.

## 🔐 Security

- Keep API keys and credentials in local environment variables.
- Never commit `.env` files or API keys to GitHub.
- Local database files are excluded from version control.

## 🎯 Future Improvements

- Add a dashboard for visualizing application progress.
- Integrate an LLM-powered assistant for personalized placement insights.
- Add reminders for pending applications and upcoming assessments.
- Export application reports to CSV.

## 👩‍💻 Author

**Aisha Anand**

M.Tech Computer Science and Engineering

- GitHub: [AISHAANAND](https://github.com/AISHAANAND)
- LinkedIn: [Aisha Anand](https://www.linkedin.com/in/aisha-anand-140a762a6)

---

⭐ If you find this project useful, consider giving the repository a star!