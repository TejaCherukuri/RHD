#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Teja Cherukuri
"""

# Python code to illustrate Sending mail with attachments
# from your Gmail account

# libraries to be imported
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import COMMASPACE, formatdate
from aws.aws_utils import AWSUtils
import os

AUTH_TOKEN = os.getenv("RHD_MAIL_AUTH_TOKEN")

def send_email(to_addr, name, test, result):

    from_addr = "rhd.reports@gmail.com"
    # report_path = "static/Reports/"+name+".pdf"

    # Define the S3 path for the PDF report
    pdf_key = f"static/reports/{name}.pdf"
    
    # Load the PDF report from S3
    report_obj = AWSUtils.load_file_from_s3(pdf_key)
    if report_obj is None:
        print(f"Failed to load report from S3: {pdf_key}")
        return
    print("Report fetched from S3")

    # instance of MIMEMultipart
    msg = MIMEMultipart()
    
    # storing the senders email address
    msg['From'] = from_addr
    
    # storing the receivers email address
    msg['To'] = COMMASPACE.join(to_addr)
    
    # message date
    msg['Date'] = formatdate(localtime=True)
    
    # storing the subject
    msg['Subject'] = "RHD Report of "+name+" for - "+ test
    
    # string to store the body of the mail
    body = 'Hello,\n\nDiagnosis report of '+name+' for '+test+' is ready. Please find the attached report and diagnosis result. \n\nDiagnosis Result: '+result+'\n\nCorrelate the information clinically. \n\nNote: Write to rhd.reports@gmail.com for any queries \n\nThanks & Regards,\nRetinal Health Diagnostics.'  
    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    
    # open the file to be sent
    # attachment = open(report_path, "rb")

    # Load the PDF report content from S3
    pdf_content = report_obj.read()
    
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
    
    # To change the payload into encoded form
    # p.set_payload((attachment).read())
    p.set_payload(pdf_content)
    
    # encode into base64
    encoders.encode_base64(p)
    
    p.add_header('Content-Disposition', "attachment; filename= %s" % name+"_"+formatdate(localtime=True)+".pdf")
    
    # attach the instance 'p' to instance 'msg'
    msg.attach(p)
    
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    
    # start TLS for security
    s.starttls()
    
    # Authentication
    s.login(from_addr, AUTH_TOKEN)
    
    # Converts the Multipart msg into a string
    text = msg.as_string()
    
    # sending the mail
    s.sendmail(from_addr, to_addr, text)

    print("Email sent!")
    
    # terminating the session
    s.quit()
