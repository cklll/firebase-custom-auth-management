from utils.mailgun import Mailgun
import unittest, json

class TestMailgun(unittest.TestCase):
    def test_should_success(self):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)        

        m = Mailgun(api_key = config['mailgun-api-key'], domain_name = config['mailgun-domain-name'])

        success = m.send_single_email(from_email_account = '{from_email_account}'.format(from_email_account = 'test-sender'),
                            from_name = '',
                            to_email = 'test-recipient@{domain_name}'.format(domain_name = config['mailgun-domain-name']),
                            to_name = '',
                            subject = 'Mailgun Test',
                            body = '''
Hello,

This is an mailgun tests.

Thank you.''')

        self.assertEqual(success, True)

    def test_incorrect_api_key(self):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)        

        m = Mailgun(api_key = "abc", domain_name = config['mailgun-domain-name'])

        success = m.send_single_email(from_email_account = '{from_email_account}'.format(from_email_account = 'test-sender'),
                            from_name = '',
                            to_email = 'test-recipient@{domain_name}'.format(domain_name = config['mailgun-domain-name']),
                            to_name = '',
                            subject = 'Mailgun Test',
                            body = '''Hello,

API key is not correct. This should not be sent.

Thank you.''')

        self.assertEqual(success, False)

    def test_incorrect_domain_name(self):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)        

        m = Mailgun(api_key = "abc", domain_name = 'incorrect.domain.com')

        success = m.send_single_email(from_email_account = '{from_email_account}'.format(from_email_account = 'test-sender'),
                            from_name = '',
                            to_email = 'test-recipient@{domain_name}'.format(domain_name = config['mailgun-domain-name']),
                            to_name = '',
                            subject = 'Mailgun Test',
                            body = '''Hello,

domain name is not correct. This should not be sent.

Thank you.''')

        self.assertEqual(success, False)


if __name__ == "__main__":
    unittest.main()