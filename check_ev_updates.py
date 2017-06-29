
import requests
import sys
import os
import time
from zipfile import ZipFile
from StringIO import StringIO
from slackclient import SlackClient
import pandas as pd

# Save your Slack token as an environment variable
slack_client = SlackClient(os.environ["SLACK_TOKEN"])

def main():

    slack_channel_name = 'ev-data-updates'
    # slack_channel_name = 'vespa' # channel for debugging 

    # Patterns for URLs
    todays_clark_url = 'https://elections.clarkcountynv.gov/VoterRequests/EVMB/ev' + time.strftime("%Y%m%d") + '.zip'
    clark_av_url = 'http://elections.clarkcountynv.gov/voterrequests/evmb/mbreq16G.zip'
    todays_washoe_url = 'https://www.washoecounty.us/voters/files/16_general_ab_ev_list/16_gen_ab_ev_list_' + time.strftime("%m_%d") + '_16.xlsx'

    # These should all be set to False at the start of the day
    # False means we'll check for them
    clark_ev_file_available = False
    clark_av_file_available = False
    washoe_file_available = False

    # Check for files every 60 seconds until they are all available
    while not clark_ev_file_available or not clark_av_file_available or not washoe_file_available: 

        print '\n' + time.strftime("%I:%M:%S %p")

        # Only check a county in the hour when they've typically posted files
        hour = int(time.strftime('%H'))

        if not clark_ev_file_available and hour >= 21: 
            clark_ev_file_available = poll_clark(todays_clark_url)
    
            if clark_ev_file_available:
                print 'Clark EV file updated!'
                send_message(slack_channel_name, 'Clark County', 'EV file available: ' + todays_clark_url)


        if not clark_av_file_available and hour >= 21: 
            clark_av_file_available = poll_clark(clark_av_url)
    
            if clark_av_file_available:
                print 'Clark AV file updated!'
                send_message(slack_channel_name, 'Clark County', 'VBM file available: ' + clark_av_url)


        if not washoe_file_available and hour >= 18: 
            washoe_file_available = poll_washoe(todays_washoe_url)

            if washoe_file_available:
                print 'Washoe file updated!'
                send_message(slack_channel_name, 'Washoe County', 'EV file available: ' + todays_washoe_url)

        time.sleep(60) 



def send_message(channel_id, user, message):
    """
    Send a message to a Slack channel
    """
    
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


def poll_clark(url):
    """
    Check when the Clark County file was last modified. 
    If the modified_at for the URL is today, return True. otherwise False
    """

    print '\nrequesting : ' + url
    r = requests.get(url, stream=True)

    modified_at = pd.to_datetime(r.headers['Last-Modified']).tz_localize('UTC').tz_convert('US/Pacific')
    print 'modified at: {}'.format(modified_at)
    
    return modified_at.date() == pd.to_datetime('today').date()


def poll_washoe(url): 
    """
    Check whether the Washoe County file exists. 
    If the URL exists, return True. otherwise False. 

    TODO: find a way to handle timeouts
    """

    print 'requesting : ' + url
    r = requests.get(url, stream=True)
    print 'status     : {}'.format(r.status_code)

    return r.status_code == requests.codes.ok



if __name__ == "__main__":
    main()
