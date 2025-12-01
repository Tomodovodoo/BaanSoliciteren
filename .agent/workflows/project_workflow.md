# Project Update Workflow

Follow these steps to update the project with new emails and status changes.

1.  **Fetch Emails**
    Run the script to fetch new emails from the server.

    ```bash
    python scripts/fetch_emails.py
    ```

2.  **Organize Emails**
    Filter and move application-related emails to the `Ongoing` folder.

    ```bash
    python scripts/organize_emails.py
    ```

3.  **Update Statistics**
    Update the `stats.json` file based on the current state of applications.

    ```bash
    python scripts/update_stats.py
    ```

4.  **Manual Updates**
    - Check the `Email/Ongoing` folder for new emails.
    - For each new email, update the `Notes` field in the corresponding `relevant_info.json` file.
    - Update the `NextAction` field in `stats.json` if necessary.
