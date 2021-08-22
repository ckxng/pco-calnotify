import unittest
import sendlib

from mock import patch


class TestSendlib(unittest.TestCase):
    def test_sendmail(self):
        mailto = "to@example.com"
        with patch('sendlib.SendGridAPIClient.send') as sender:
            sender.return_value.status_code = 200
            sender.return_value.body = "Mock Success"
            sender.return_value.headers = "Mock-Header: Success"

            self.assertEqual(sendlib.sendmail(mailto, "Subject", "Text", "KEY", "from@example.com"), None)
            self.assertRaises(KeyError, sendlib.sendmail, mailto, "Subject", "Text", "KEY")
            self.assertRaises(KeyError, sendlib.sendmail, mailto, "Subject", "Text")

            with patch('sendlib.os.environ') as env:
                env['SENDGRIDAPIKEY'] = 'KEY'
                env['MAILFROM'] = 'from@example.com'

                self.assertEqual(sendlib.sendmail(mailto, "Subject", "Text"), None)

    def test_sendsms(self):
        smsto = "+15551234567"
        with patch('sendlib.Client.messages') as sender:
            sender.create = lambda **kw: type('', (object,), {"sid": 1})()

            self.assertEqual(sendlib.sendsms(smsto, "Text", "SID", "TOKEN", "SERVICESID"), None)
            self.assertRaises(KeyError, sendlib.sendsms, smsto, "Text", "SID", "TOKEN")
            self.assertRaises(KeyError, sendlib.sendsms, smsto, "Text", "SID")
            self.assertRaises(KeyError, sendlib.sendsms, smsto, "Text")

            with patch('sendlib.os.environ') as env:
                env['TWILIOSID'] = 'SID'
                env['TWILIOTOKEN'] = 'TOKEN'
                env['TWILIOSERVICESID'] = 'SERVICESID'

                self.assertEqual(sendlib.sendsms(smsto, "Text"), None)


if __name__ == '__main__':
    unittest.main()
