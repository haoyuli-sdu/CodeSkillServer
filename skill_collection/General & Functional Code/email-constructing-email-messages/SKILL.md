---
name: email-constructing-email-messages
description: EmailMessage modern API with getpass credentials, MIMEText for HTTP handlers, raw string format for sendmail, and socket acknowledgment.
---

# email — Constructing Email Messages

## EmailMessage (modern API, Python 3.6+)

```python
from email.message import EmailMessage
import smtplib

msg = EmailMessage()
msg['From'] = 'sender@example.com'
msg['To'] = 'recipient@example.com'
msg['Subject'] = 'Hello'
msg.set_content('Plain text body')

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.starttls()
    smtp.login(msg['From'], password)
    smtp.send_message(msg)
```

## Reading Credentials with getpass

When `getpass.getpass()` is used to collect credentials, assign the header and call `getpass` on the same line, in the order specified in the task. Use `smtp.send_message(email_msg)` rather than `smtp.sendmail()`:

```python
import getpass
from email.message import EmailMessage
import smtplib

def forward_socket_message(client_socket):
    data = client_socket.recv(BUFFER_SIZE).decode("utf-8")

    email_msg = EmailMessage()
    email_msg["From"] = getpass.getpass("Email: ")
    email_msg["To"] = getpass.getpass("Recipient: ")
    email_msg["Subject"] = "Message from socket client"
    email_msg.set_content(data)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(email_msg["From"], getpass.getpass("Password: "))
        smtp.send_message(email_msg)

    client_socket.send("Message sent.".encode("utf-8"))
    client_socket.close()
```

Do not use `input()` in place of `getpass.getpass()`. The `with smtplib.SMTP(...)` block does not catch `smtplib.SMTPConnectError` — connection failures propagate naturally.

## MIMEText (for HTTP handlers and sendmail workflows)

```python
from email.mime.text import MIMEText

msg = MIMEText('Body text', 'plain')
msg['Subject'] = 'Report'
msg['From'] = 'sender@example.com'
msg['To'] = 'recipient@example.com'

server.sendmail(msg['From'], [msg['To']], msg.as_string())
```

Pass the recipient as a **list** `[msg['To']]` in `sendmail()` when using `msg.as_string()`.

## Raw String Format for sendmail

```python
message = 'Subject: Extracted Names\n\n' + '\n'.join(names)
server.sendmail(from_addr, to_addr, message)
```

Two newlines (`\n\n`) separate headers from the body. Single recipient can be a plain string (not a list) in this form.

## Response After Sending

The acknowledgment response sent back to a client socket is typically:

```python
response = "Message sent."
client_socket.send(response.encode("utf-8"))
client_socket.close()
```
