import shutil
import smtplib
import platform
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# Configuration
THRESHOLD_PERCENT = 15
EMAIL_TO = "rowlettron@yahoo.com"
EMAIL_FROM = "your_email@example.com"
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@example.com"
SMTP_PASSWORD = "your_password"

def get_disk_usage():
    drives = []
    system = platform.system()

    if system == "Windows":
        for drive_letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = f"{drive_letter}:\\"
            if Path(drive).exists():
                usage = shutil.disk_usage(drive)
                drives.append((drive, usage))
    else:
        mount_points = [Path("/")] + list(Path("/Volumes").glob("*"))
        for mount in mount_points:
            if mount.is_dir():
                try:
                    usage = shutil.disk_usage(str(mount))
                    drives.append((str(mount), usage))
                except:
                    continue
    return drives

def check_threshold(drives):
    alerts = []
    for drive, usage in drives:
        percent_free = (usage.free / usage.total) * 100
        if percent_free < THRESHOLD_PERCENT:
            alerts.append(f"Drive {drive} is below {THRESHOLD_PERCENT}% free space. Only {percent_free:.2f}% remaining.")
    return alerts

def send_email(alerts):
    subject = "Disk Space Alert"
    body = "\n".join(alerts)

    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print("Alert email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    drives = get_disk_usage()
    alerts = check_threshold(drives)
    if alerts:
        send_email(alerts)
    else:
        print("All drives have sufficient free space.")

if __name__ == "__main__":
    main()
