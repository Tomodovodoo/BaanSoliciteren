---
description: Update the project by fetching emails, organizing them, and updating stats.
---

# Project Update Workflow

Follow these steps to update the project with new emails and status changes.

1.  **Fetch Emails**
    Run the script to fetch new emails from the server.
    // turbo

    ```bash
    python scripts/fetch_emails.py
    ```

2.  **Manual Email Processing**

    - Check `Email/Processing` for fetched emails.
    - Identify unrelated emails (spam/notifications) and set `"company": "DISCARD"` in the JSON file.
    - Identify valid application emails and set `"company"` (exact folder name) and `"response"` (e.g., "Received", "Rejected", "Interview Scheduled") in the JSON file.

3.  **Organize Emails**
    Filter and move application-related emails to the `Ongoing` folder.
    // turbo

    ```bash
    python scripts/organize_emails.py
    ```

4.  **Update Statistics**
    Update the `stats.json` file based on the current state of applications.

    ```bash
    python scripts/update_stats.py
    ```

5.  **Archive Rejected Jobs**
    Move job folders with 'Rejected' or 'Expired' status to the Archive directory.
    // turbo

    ```bash
    python scripts/archive_jobs.py
    ```

6.  **Manual Follow-up**

    - Check the `Email/Ongoing` folder for new emails.
    - For each new email, update the `Notes` field in the corresponding `relevant_info.json` file.
    - Update the `NextAction` field in `stats.json` if necessary.

7.  **Update Cover Letter Database**
    Run the script to extract cover letters from rejected jobs and update the knowledge base.
    // turbo
    ```bash
    python scripts/extract_previous_letters.py
    ```
