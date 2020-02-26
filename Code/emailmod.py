import smtplib

def send_email(recipient, body):
    ## This simply sends an email to an email address 'recipient' to allow them
    ## to reset their password

    ## 'message' is the complete message to be sent with headers for from, to,
    ## subject and the body of the email
    message = "\r\n".join([
        "From: simulatorpassrst@gmail.com",
        "To: {}".format(recipient),
        "Subject: Password Reset",
        "",
        "{}".format(body)])

    ## Establishes a connection to Google's Gmail SMTP email server on port 587
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    ## Logins into the server using a Gmail account created specifically for this task
    server.login("simulatorpassrst@gmail.com", "SecurePass123")
    ## Sends the email using a try except block; if the email is rejected for any reason
    ## the function will simply return False rather than error out
    ## The program then logs out of the email server
    try:
        server.sendmail("simulatorpassrst@gmail.com",
                        recipient,
                        message)
        server.quit()
    except:
        server.quit()
        return False

    
