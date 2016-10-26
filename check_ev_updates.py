
import requests
import sys
import os
import time
from zipfile import ZipFile
from StringIO import StringIO
from slackclient import SlackClient
# import shutil

print 'helloworld'

slack_client = SlackClient(os.environ["SLACK_TOKEN"])

def main():

    slack_channel_name = 'vespa' # testing
    # slack_channel_name = 'ev-data-updates'
    
    # todays_clark_url = 'https://elections.clarkcountynv.gov/VoterRequests/EVMB/ev20161024.zip'
    todays_clark_url = 'https://elections.clarkcountynv.gov/VoterRequests/EVMB/ev' + time.strftime("%Y%m%d") + '.zip'

    # todays_washoe_url = 'https://www.washoecounty.us/voters/files/16_general_ab_ev_list/16_gen_ab_ev_list_10_24_16.xlsx'
    todays_washoe_url = 'https://www.washoecounty.us/voters/files/16_general_ab_ev_list/16_gen_ab_ev_list_' + time.strftime("%m_%d") + '_16.xlsx'

    print 'Looking for file: ' + todays_clark_url
    print 'Looking for file: ' + todays_washoe_url

    clark_file_available = False
    washoe_file_available = True

    while not clark_file_available or not washoe_file_available: 

        if not clark_file_available: 
            clark_file_available = poll_clark(todays_clark_url)
    
            if clark_file_available:
                print 'Clark file updated!'
                send_message(slack_channel_name, 'Clark County', 'EV file available: ' + todays_clark_url)


        if not washoe_file_available: 
            washoe_file_available = poll_washoe(todays_washoe_url)

            if washoe_file_available:
                print 'Washoe file updated!'
                send_message(slack_channel_name, 'Washoe County', 'EV file available: ' + todays_washoe_url)

        time.sleep(60) 


def send_message(channel_id, user, message):
    
    response = slack_client.api_call(
        "chat.postMessage",
        channel=channel_id,
        text=message,
        username=user,
        icon_emoji=':robot_face:'
    )
    
    if response['ok']: 
        print 'Message posted to Slack.'
    else: 
        sys.exit('Message not sent. Slack error: ' + response['error'])


def poll_clark(todays_clark_url):

    r = requests.get(todays_clark_url, stream=True)

    if 'No data available yet' in r.content[0:100]: 
        print time.strftime("%I:%M:%S %p") + ' - Clark nada'
        return False
    else: 
        return True

def poll_washoe(todays_washoe_url): 

    r = requests.get(todays_washoe_url, stream=True)

    if r.status_code == requests.codes.ok: 
        return True
    else: 
        print time.strftime("%I:%M:%S %p") + ' - Washoe nada'
        return False



if __name__ == "__main__":
    main()
