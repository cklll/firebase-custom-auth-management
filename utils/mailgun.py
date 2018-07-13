import requests

class Mailgun:
    def __init__(self, api_key, domain_name):      
        self.api_key = api_key
        self.domain_name = domain_name

    def send_single_email(self, from_email_account, from_name, to_email, to_name, subject, body):
        response = requests.post(
                "https://api.mailgun.net/v3/{domain_name}/messages".format(domain_name = self.domain_name),
                auth=("api", self.api_key),
                data={
                    "from": "{from_name} <{from_email_account}@{domain_name}>".format(from_name = from_name, from_email_account = from_email_account, domain_name = self.domain_name),
                    "to": ["{to_name} {to_email}".format(to_name = to_name, to_email = to_email)],
                    "subject": subject,
                    "text": body})

        return True if response.status_code == 200 else False
