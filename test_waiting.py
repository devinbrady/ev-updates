# test_waiting.py


import sys
import os
import time
from slackclient import SlackClient

slack_client = SlackClient(os.environ["SLACK_TOKEN"])


def main():

    for i in range(0,10): 
        print i
        time.sleep(10)
        # send_message('vespa', 'George Michael', ':walking:', 'I have Pop Pop in the attic.') 
        send_message('vespa', 'George Michael', ':walking:', 'If I fail math, there goes my chance at a good job and a happy life full of hard work.') 


def send_message(channel_id, user='Bot', icon_emoji=':robot_face:', message='Test message.'):
    
    response = slack_client.api_call(
        "chat.postMessage",
        channel=channel_id,
        text=message,
        username=user,
        icon_emoji=icon_emoji
    )
    
    if response['ok']: 
        print 'Message posted to Slack.'
    else: 
        sys.exit('Message not sent. Slack error: ' + response['error'])


if __name__ == "__main__":
    main()
