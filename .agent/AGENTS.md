# BaanSoliciteren - Agent Guide

Welcome to the **BaanSoliciteren** project. This project is a semi-automated job application tracking system that synchronizes email communications with structured JSON data.

## How it Works

The system manages job applications by cross-referencing folders in `Solicitaties/` with email data in `Email/`.

1. **Information Extraction**: Job details (location, deadline, link, contact) are stored in `relevant_info.json`.
2. **Status Tracking**: The "state of play" is stored in `stats.json`.
3. **Email Integration**: Emails are fetched from Gmail and triaged into job-specific folders.
4. **Logic & Automation**: Scripts analyze deadlines and email responses to automatically update the status of each application.
5. **Knowledge Base**: Previously sent cover letters are extracted and stored in `data/Vorige solicitatie brieven.json` for future reference.

## Application States

### Active (Ongoing) Applications

- **Location**: `Email/Ongoing/[Job_Folder_Name]`
- **Definition**: Applications that are currently being prepared, submitted, or are awaiting a response.
- **Statuses**: `Unsent`, `Called`, `Pending`, `Received`, `Interview Scheduled`, `Offer`.
- **Logic**: If an application has `Unsent` or `Called` status but the deadline has passed, it is eligible to be marked as **Expired**.

### Archived Applications

- **Location**: `Email/Archive/[Job_Folder_Name]`
- **Definition**: Applications that have reached a final state.
- **Statuses**: `Rejected`, `Expired`, `Hired`, `Other`.
- **Auto-Archiving**: The system automatically moves all emails for a job to the `Archive` directory once a final state is detected (e.g., a "Rejected" email response or a manual rejection in `stats.json`).

## Core Scripts

- **`fetch_emails.py`**: Downloads relevant emails from Gmail to `Email/Processing/`.
- **`organize_emails.py`**: Moves emails from `Processing` to the correct `Ongoing` or `Archive` job folder based on manual or automatic tags.
- **`update_stats.py`**: The central update logic.
  - Synchronizes `stats.json` with the latest email responses.
  - Implements **Final State Priority**: Final states like `Rejected` always override non-final states like `Received`.
  - Handles **Deadline Expiration**: Automatically marks applications as `Expired` if the deadline has passed and no contact was made.
- **`extract_previous_letters.py`**: Extracts `Motivatie.txt` contents from archived job folders and stores them in `data/Vorige solicitatie brieven.json`. This acts as a database of your previous application styles and arguments.

## Task & Implementation Documentation

For detailed history on specific technical upgrades and tasks performed by AI agents, refer to the following documentation (Paths relative to agent's brain directory):

- **Current Task List**: [task.md](file:///C:/Users/Tom/.gemini/antigravity/brain/dfa80b1e-33be-4a04-8b48-0568efb5d07e/task.md)
- **Detailed Design & Implementation Plans**: [implementation_plan.md](file:///C:/Users/Tom/.gemini/antigravity/brain/dfa80b1e-33be-4a04-8b48-0568efb5d07e/implementation_plan.md)
- **Verification & Proof of Work**: [walkthrough.md](file:///C:/Users/Tom/.gemini/antigravity/brain/dfa80b1e-33be-4a04-8b48-0568efb5d07e/walkthrough.md)

## Common Workflows

- Run `python scripts/update_stats.py` to keep all application statuses and archives in sync.
- Use the `/update_project` slash command to run the full fetch-organize-update sequence.
