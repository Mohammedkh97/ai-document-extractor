# Frappe Integration Plan

This guide details the steps to integrate the AI Document Extractor with your Frappe/HRMS instance (`https://hrms.pro-shazmlc.cloud`).

## 1. Frappe Authentication Setup

To allow the Python application to read/write data to Frappe, you need to create an API Key and Secret.

1.  Login to **Desk** > **User List**.
2.  Open the User account you want to use (or create a dedicated "AI Bot" user).
3.  Go to the **API Access** section.
4.  Click **Generate Keys** (if not already generated).
5.  Copy the **API Key** and **API Secret**.
6.  Update your local `.env` file with these values:
    ```bash
    FRAPPE_API_KEY=your_api_key
    FRAPPE_API_SECRET=your_api_secret
    ```

## 2. DocType Setup

The application expects to read a document (PDF) and write back extracted fields. We recommend creating a dedicated DocType or extending an existing one.

### Option A: dedicated "AI Extraction Request" (Recommended)

Create a new DocType with the following fields:

- `naming_series` (Data, e.g., "AI-EXT-.YYYY.-")
- `document_file` (Attach) - _This is where you upload the PDF_
- `status` (Select: "Pending", "Processing", "Completed", "Failed")
- `extracted_data` (Code/JSON) - _To store the raw JSON result_
- **Extracted Fields** (Data/Date):
  - `document_type` (Data)
  - `full_name` (Data)
  - `passport_number` (Data)
  - `date_of_birth` (Date)
  - `nationality` (Data)
  - ... (add other fields you expect from your schemas)

### Option B: Extend an existing DocType (e.g., "Employee")

Ensure the DocType has an "Attach" field for the document and fields to map the results to.

## 3. Webhook / Server Script Integration

You need to trigger the extraction when a file is uploaded.

### Method 1: Server Script (Recommended)

1.  Go to **Server Script** list.
2.  Create a new Script:
    - **Script Type**: DocType Event
    - **DocType**: `AI Extraction Request` (or your chosen DocType)
    - **Doc Event**: After Save
3.  **Script**:

    ```python
    # URL of your Python AI App (must be reachable from the Frappe server)
    # If running locally, you might need a tunnel (ngrok) or use the internal IP if dockerized.
    ai_app_url = "http://host.docker.internal:8000" # or your public URL

    if doc.document_file and doc.status == "Pending":
        try:
            # Prepare payload
            payload = {
                "doctype": doc.doctype,
                "docname": doc.name,
                "document_url": frappe.utils.get_url(doc.document_file), # Gets full URL
                "attachment_field": "document_file"
            }

            # Send request to AI App
            response = frappe.make_post_request(
                url=f"{ai_app_url}/api/v1/webhooks/frappe",
                data=payload
            )

            frappe.msgprint("AI Extraction Started!")

        except Exception as e:
            frappe.log_error(f"AI Extraction Failed: {str(e)}")
    ```

## 4. Testing the Connection

1.  **Start your AI App**:
    ```bash
    uvicorn app.main:app --reload
    ```
2.  **Verify Connectivity**:
    Ensure `https://hrms.pro-shazmlc.cloud` is accessible from where the python app is running.

    _Current Configuration_:
    - **Frappe URL**: `https://hrms.pro-shazmlc.cloud`
    - **OCR Provider**: `openai`
    - **LLM Model**: `gpt-4o`

3.  **Run a Test**:
    You can manually test it using `curl` if you have a DocName ready in Frappe:

    ```bash
    curl -X POST "http://localhost:8000/api/v1/webhooks/frappe" \
         -H "Content-Type: application/json" \
         -d '{
               "doctype": "AI Extraction Request",
               "docname": "AI-EXT-2024-00001",
               "attachment_field": "document_file"
             }'
    ```

## 5. Next Steps

Once you provide the **API Key** and **Secret**, we can run a script to verify the connection from this app to your Frappe instance.
