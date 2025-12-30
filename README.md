Pinterest Analytics Parser

**Automated Pinterest performance tracking with Google Sheets synchronization**

<img width="1260" height="682" alt="Screenshot_2" src="https://github.com/user-attachments/assets/078638bb-7ee4-4ec0-b4f6-8346bb65974a" />

**Overview**

**Pinterest Analytics Parser** is a Python-based automation tool that collects analytics data from a Pinterest account and synchronizes it with Google Sheets.

The project is designed for:
- **Long-term analytics**
- **Stable execution**
- **Safe API usage within Pinterest limits**

> **Goal:** Track content performance without overwriting historical data.

**Key Features**

- **Automatic scanning** of all Pinterest boards  
- **Detection of new pins** and appending them to Google Sheets  
- **Updating analytics** for existing pins  
- **Content type detection** (**Video / Post**)  
- **Rate-limit safe requests**  
- **Fully automated scheduling** (every 3 hours)  
- **No hardcoded secrets** — everything stored in `.env`


**Data Collected**

Each Pinterest pin is stored with the following fields:

- **Publish date**
- **Pin title** (trimmed if too long)
- **Content type** (**Video** or **Post**)
- **Impressions**
- **Pin clicks**
- **Pinterest Pin ID** (**unique identifier**)

> **Pin ID acts as a primary key** to prevent duplicates and ensure safe updates.


**Technical Details**

- **Language:** Python  
- **API:** Pinterest API v5  
- **Storage:** Google Sheets  
- **Execution:** Scheduled background task  


**Technology Stack**

- **Python**
- **Pinterest API v5**
- **Google Sheets API**
- **requests**
- **gspread**
- **google-auth**
- **python-dotenv**
- **schedule**


**Configuration (.env)**

All sensitive data is loaded from `.env`:
SERVICE_ACCOUNT_FILE=
PINTEREST_ACCESS_TOKEN=
PINTEREST_SHEET_NAME=
SPREADSHEET_ID=

> **Security note:** No credentials are stored in the source code.
>
> ## Execution Logic

1. **Load environment variables**
2. **Authenticate** with Pinterest and Google Sheets
3. **Fetch boards and pins**
4. **Request analytics** for the last **89 days**
5. **Detect new or existing pins**
6. **Append or update rows**
7. **Repeat every 3 hours**

---------------------------------------------

**Intended Use**

This project is suitable for:

- **Content creators**
- **Marketing analytics**
- **Pinterest performance tracking**
- **Automated reporting systems**
