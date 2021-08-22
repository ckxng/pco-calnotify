import unittest

from mock import patch

import sendlib


class TestSendlib(unittest.TestCase):
    def test_sendmail(self):
        mailto = "to@example.com"
        patch_environ = 'sendlib.os.environ'
        with patch('sendlib.SendGridAPIClient.send'):
            self.assertEqual(sendlib.sendmail(mailto, "Subject", "Text", "KEY", "from@example.com"), None)
            self.assertRaises(KeyError, sendlib.sendmail, mailto, "Subject", "Text", "KEY")
            self.assertRaises(KeyError, sendlib.sendmail, mailto, "Subject", "Text")

            with patch(patch_environ) as env:
                env['SENDGRIDAPIKEY'] = 'KEY'
                env['MAILFROM'] = 'from@example.com'

                self.assertEqual(sendlib.sendmail(mailto, "Subject", "Text"), None)

            with patch(patch_environ) as env:
                env.get = lambda x, y: '1'

                self.assertEqual(sendlib.sendmail(mailto, "Subject", "Text", "KEY", "from@example.com"), None)

    def test_sendsms(self):
        smsto = "+15551234567"
        patch_environ = 'sendlib.os.environ'
        with patch('sendlib.Client.messages'):
            self.assertEqual(sendlib.sendsms(smsto, "Text", "SID", "TOKEN", "SERVICESID"), None)
            self.assertRaises(KeyError, sendlib.sendsms, smsto, "Text", "SID", "TOKEN")
            self.assertRaises(KeyError, sendlib.sendsms, smsto, "Text", "SID")
            self.assertRaises(KeyError, sendlib.sendsms, smsto, "Text")

            with patch(patch_environ) as env:
                env['TWILIOSID'] = 'SID'
                env['TWILIOTOKEN'] = 'TOKEN'
                env['TWILIOSERVICESID'] = 'SERVICESID'

                self.assertEqual(sendlib.sendsms(smsto, "Text"), None)

            with patch(patch_environ) as env:
                env.get = lambda x, y: '1'

                self.assertEqual(sendlib.sendsms(smsto, "Text", "SID", "TOKEN", "SERVICESID"), None)


if __name__ == '__main__':
    unittest.main()
