---
name: getpass-secure-credential-input
description: 'Guide for getpass.getpass() usage: collecting credentials without echoing, socket+email integration, and EmailMessage API.'
---

# getpass — Secure Credential Input

## Core API

`getpass.getpass(prompt)` prompts for input **without echoing** typed characters. It works in terminals and is the correct tool for passwords, email addresses, and any other sensitive strings collected interactively. It returns the entered string.

```python
import getpass

password = getpass.getpass("Password: ")        # typed characters hidden
email = getpass.getpass("Email: ")              # any prompt string works
```

Unlike `input()`, `getpass.getpass()` suppresses terminal echo and is the appropriate function for collecting any credential string — email addresses, usernames, or passwords. Use `getpass.getpass()` for all credential fields, not `input()`.

## Socket + Email Pattern

Receive data from a socket, collect credentials with `getpass.getpass()`, send an email, then send a brief confirmation reply and close the socket:

```python
import smtplib
from email.message import EmailMessage
import getpass

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
BUFFER_SIZE = 1024

def handle_socket_email(client_socket):
    request = client_socket.recv(BUFFER_SIZE).decode("utf-8")

    email_msg = EmailMessage()
    email_msg["From"] = getpass.getpass("Email: ")
    email_msg["To"] = getpass.getpass("Recipient: ")
    email_msg["Subject"] = "Message from socket client"
    email_msg.set_content(request)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(email_msg["From"], getpass.getpass("Password: "))
        smtp.send_message(email_msg)

    client_socket.send("Message sent.".encode("utf-8"))
    client_socket.close()
```

Key points:
- All three prompts (sender email, recipient email, password) use `getpass.getpass()`.
- Set `email_msg["From"]` before `smtp.login()` so credentials are consistent.
- After sending the email, send a short status reply and close the socket.

## EmailMessage API

`email.message.EmailMessage` is the modern Python 3.6+ API:
- Set body: `msg.set_content(text)`
- Set headers: `msg["From"] = ...`, `msg["To"] = ...`, `msg["Subject"] = ...`
- Send: `smtp.send_message(msg)` (works with `EmailMessage` objects)

`smtplib.SMTP` context manager pattern: use `starttls()` before `login()` for port 587 (STARTTLS upgrade). Do not call `starttls()` when using port 465 (SSL).
