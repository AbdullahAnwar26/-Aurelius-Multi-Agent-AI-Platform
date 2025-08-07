from crewai.tools import tool
from typing import Optional
import os, ssl, re, smtplib
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import re
from .log_in import email, password  

def user_login(email: str = email, password: str = password):
    user_email= email
    user_password = password
    return user_email, user_password

@dataclass
class EmailConfig:
    email: str
    password: str
    smtp_server: str
    smtp_port: int
    use_tls: bool = True



def select_email_config_by_user_email(email: str, password: str) -> EmailConfig:
    domain = email.split('@')[-1].lower()
    smtp_map = {
        "gmail.com": "smtp.gmail.com",
        "outlook.com": "smtp-mail.outlook.com",
        "hotmail.com": "smtp-mail.outlook.com",
        "yahoo.com": "smtp.mail.yahoo.com",
        "zoho.com": "smtp.zoho.com",
        "icloud.com": "smtp.mail.me.com"
    }
    if domain not in smtp_map:
        raise ValueError(f"Unsupported email domain: {domain}")
    return EmailConfig(email, password, smtp_map[domain], 465, True)


def clean_markdown(text: str) -> str:
    """
    Removes common Markdown syntax like **, #, *, and inline links.
    """
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # bold
    text = re.sub(r'__([^_]+)__', r'\1', text)    # underline
    text = re.sub(r'[*_]{1,2}', '', text)         # *, _, **, __
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # headers
    text = re.sub(r'^[-=]+\n', '', text, flags=re.MULTILINE)  # hr
    text = re.sub(r'^\s*[*-]\s+', '  - ', text, flags=re.MULTILINE)  # bullets
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 [\2]', text)  # [text](url) → text [url]
    return text.strip()

@tool
def send_email_smtp(
    query: str,
    file_path: Optional[str] = None,
    csv_file: Optional[str] = None,
    report_content: Optional[str] = None
) -> str:
    """
    Sends an email using SMTP. Supports single or bulk (CSV) sending.
    Can attach files and send pre-generated report content as the message body.
    
    Inputs:
    - query: The original instruction text (used for fallback parsing).
    - file_path: Path to a file to attach.
    - csv_file: Path to a CSV file with column 'Emails'.
    - report_content: Optional content (e.g., generated report) to use as message body.

    SMTP credentials are currently hardcoded for testing (to be parameterized securely).
    """
    
    user_email, user_password = user_login()
    try:
        config = select_email_config_by_user_email(user_email, user_password)
    except Exception as e:
        return f"SMTP Config Error: {str(e)}"

    # Extract recipient, subject, message from query
    to_match = re.search(r'to\s+([\w\.-]+@[\w\.-]+)', query)
    subject_match = re.search(r"subject\s+'([^']+)'", query)
    
    message_match = re.search(r"(?:message|send this message|write this message)\s+'([^']+)'", query, re.IGNORECASE)
    fallback_message = message_match.group(1) if message_match else None

    # Combine both user and AI-generated content
    combined_message_parts = []

    if fallback_message:
       combined_message_parts.append(fallback_message.strip())

    if report_content:
       combined_message_parts.append(report_content.strip())

    if not combined_message_parts:
       return "Error: No message content found in query or generated content."

    raw_message = "\n\n".join(combined_message_parts)
    message_body = clean_markdown(raw_message)





    # ATTACHMENT block
    def attach_file_to_msg(msg):
        if file_path:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Attachment not found: {file_path}")
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
            msg.attach(part)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(config.smtp_server, config.smtp_port, context=context) as server:
            server.login(config.email, config.password)

            if csv_file:
                if not os.path.exists(csv_file):
                    return f"CSV file not found at {csv_file}"

                recipients_df = pd.read_csv(csv_file)
                if 'Emails' not in recipients_df.columns:
                    return "CSV must contain a column named 'Emails'"

                for email in recipients_df['Emails']:
                    msg = MIMEMultipart()
                    msg['From'] = config.email
                    msg['To'] = email
                    subject_match = re.search(r"subject\s+'([^']+)'", query)
                    subject = subject_match.group(1) if subject_match else "No Subject"
                    msg['Subject'] = subject
                    msg.attach(MIMEText(message_body, 'plain'))
                    attach_file_to_msg(msg)
                    server.sendmail(config.email, email, msg.as_string())

                return f"Email sent to {len(recipients_df)} recipients from CSV."
            
            # Single recipient
            if not to_match:
                return "Could not find a recipient in the query."
            to_email = to_match.group(1)

            msg = MIMEMultipart()
            msg['From'] = config.email
            msg['To'] = to_email
            subject_match = re.search(r"subject\s+'([^']+)'", query)
            subject = subject_match.group(1) if subject_match else "No Subject"
            msg['Subject'] = subject
            
 
            msg.attach(MIMEText(message_body, 'plain'))
            attach_file_to_msg(msg)
            server.sendmail(config.email, to_email, msg.as_string())
            return f"Email sent to {to_email}"

    except Exception as e:
        return f"SMTP Send Error: {str(e)}"
