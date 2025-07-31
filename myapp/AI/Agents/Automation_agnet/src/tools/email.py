import os
import re
import smtplib ,ssl
from typing import List, Optional
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from crewai.tools import tool
import pandas as pd

# user_email = "sk9893836@gmail.com"
# user_password = "uabysecsybpejhgt"


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


@tool
def send_email_smtp(query: str,file_path: Optional[str] = None, csv_file:Optional[str]=None) -> str:
    """
    Sends email using SMTP based on a query.
    query (str): A string with the recipient, subject, and message.
    If a CSV file is provided, it will send emails to all recipients listed in the file
    and if no CSV file is provided, it will send a single email to the specified recipient from the query.
    if in query user say to genrate report and send to the mail as message then takes generated report as message from the reprt agent and take a query also for finding the email address and subject .
    and if file_path is provided, it will attach the specified file to the email.
    Example: "to receiver@example.com with subject 'Hello' and message 'Test message or report content'".
        file_path (Optional[str]): The path to a file to attach. Defaults to None.
    Example:genrate a report on the indian media then take as message and send an email to sheikhupdesk@gmail.com with subject indian media and try to send full report and  with attached file    
    Example: send an email to emails which i provide in csv file with subject 'Hello' and message 'Hope youre doing well'    
    Eample: send an email to sheikhupdesk@gmail.com with subject indian media and message to ask about your self with file i provided
    Example : send an email to sheikhupdesk@gmail.com with subject indian media and in message write a peom on cow with attached file
    Example: genrate the report on the india it industry then send an email to emails which i provide in csv file with subject 'test' and attech the file also send
    Example : genrate the report on the india it industry then send an email to emails which i provide in csv file with subject 'test' and send attached file
    Example : generate a report on (topic by user) and send as body email to emails which are provided in csv file with subject test and with attachment picture
    Example : "generate a report on netflix india and send as body email to emails which are provided in csv file with subject test and with attachment picture"
    """

    user_email = "sk9893836@gmail.com"
    user_password = "uabysecsybpejhgt"

    if not user_email or not user_password:
        return "Missing SMTP credentials. Please configure them."

    try:
        config = select_email_config_by_user_email(user_email, user_password)
    except Exception as e:
        return f"SMTP Config Error: {str(e)}"
    
#   # Check if CSV file is provided  
    if csv_file:
        if not os.path.exists(csv_file):
               return f"Error: CSV file not found at '{csv_file}'"
        csv_email = pd.read_csv(csv_file)
        subject_match = re.search(r"subject\s+'([^']+)'", query)
        message_match = re.search(r"message\s+'([^']+)'", query)

        if not subject_match or not message_match:
               return "Error: Could not parse 'subject' or 'message' from query."

        subject = subject_match.group(1)
        message = message_match.group(1)

        msg = MIMEMultipart()
        msg['From'] = config.email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
   
        if file_path:
               if not os.path.exists(file_path):
                   return f"Error: Attachment file not found at '{file_path}'"
               try:
                   with open(file_path, "rb") as attachment:
                       part = MIMEBase("application", "octet-stream")
                       part.set_payload(attachment.read())
                   encoders.encode_base64(part)
                   part.add_header(
                       "Content-Disposition",
                       f"attachment; filename= {os.path.basename(file_path)}",
                   )
                   msg.attach(part)
               except Exception as e:
                   return f"Error attaching file: {str(e)}"

        try:
               context = ssl.create_default_context()
               server = smtplib.SMTP_SSL(config.smtp_server, config.smtp_port, context = context)
               server.login(config.email, config.password)
               for index in range(len(csv_email)):
                   msg.attach(MIMEText(message, 'plain'))
                   server.sendmail(config.email, csv_email["Emails"][index], msg.as_string())
               server.quit()
               return f"Emails sent successfully to recipients from CSV."
        except Exception as e:
               return f"SMTP Send Error: {str(e)}"   
# without csv file
    else:
        # Safe regex parsing
        to_match = re.search(r'to\s+([\w\.-]+@[\w\.-]+)', query)
        subject_match = re.search(r"subject\s+'([^']+)'", query)
        message_match = re.search(r"message\s+'([^']+)'", query)

        to_email = to_match.group(1)
        subject = subject_match.group(1)
        message = message_match.group(1)

    # Compose the message
        msg = MIMEMultipart()
        msg['From'] = config.email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
    
        if file_path:
            if not os.path.exists(file_path):
                return f"Error: Attachment file not found at '{file_path}'"
        
            try:
                with open(file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
            
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(file_path)}",
                )
                msg.attach(part)
            except Exception as e:
                return f"Error attaching file: {str(e)}"
    

        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(config.smtp_server, config.smtp_port, context = context)
            server.login(config.email, config.password)
            server.sendmail(config.email, [to_email], msg.as_string())
            server.quit()
            success_message = f"Email sent successfully to {to_email}"
            if file_path:
             success_message += f" with attachment '{os.path.basename(file_path)}'"
             return success_message
        except Exception as e:
           return f"SMTP Send Error: {str(e)}"