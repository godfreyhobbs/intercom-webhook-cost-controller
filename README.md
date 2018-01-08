# intercom-webhook-cost-controler
A Intercom Cost Control Bot - keeps your people count under limit.  This help limit monthly cost for intercom.  Also archives in dynamodb table.


# notes

Using the webhook followed by a rest call leads to the following error:

'Remote end closed connection without response: RemoteDisconnected Traceback'

Intercom webhooks retry when a failure is returned.  These intercom webhook retries seem to allow the system to recover.  I assume intercom REST api getUser takes a few seconds to catch up with the webhook.
So in short these errors can be safely ignored.



