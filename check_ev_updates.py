
import requests
import sys
import os
import time
from zipfile import ZipFile
from StringIO import StringIO
from slackclient import SlackClient
import pandas as pd


slack_client = SlackClient(os.environ["SLACK_TOKEN"])

def main():

    slack_channel_name = 'ev-data-updates'
    # slack_channel_name = 'vespa'
    
    # todays_clark_url = 'https://elections.clarkcountynv.gov/VoterRequests/EVMB/ev20161027.zip'
    todays_clark_url = 'https://elections.clarkcountynv.gov/VoterRequests/EVMB/ev' + time.strftime("%Y%m%d") + '.zip'

    clark_av_url = 'http://elections.clarkcountynv.gov/voterrequests/evmb/mbreq16G.zip'

    # todays_washoe_url = 'https://www.washoecounty.us/voters/files/16_general_ab_ev_list/16_gen_ab_ev_list_10_24_16.xlsx'
    todays_washoe_url = 'https://www.washoecounty.us/voters/files/16_general_ab_ev_list/16_gen_ab_ev_list_' + time.strftime("%m_%d") + '_16.xlsx'

    # print 'Looking for file: ' + todays_clark_url
    # print 'Looking for file: ' + todays_washoe_url

    clark_ev_file_available = True
    clark_av_file_available = False
    washoe_file_available = True


    # print time.ctime(os.path.getmtime('/Users/devin/Downloads/MBREQ16G-2.txt'))

    

    while not clark_ev_file_available or not clark_av_file_available or not washoe_file_available: 

        print '\n' + time.strftime("%I:%M:%S %p")
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

    print '\nrequesting : ' + url
    r = requests.get(url, stream=True)

    modified_at = pd.to_datetime(r.headers['Last-Modified']).tz_localize('UTC').tz_convert('US/Pacific')
    print 'modified at: {}'.format(modified_at)
    
    return modified_at.date() == pd.to_datetime('today').date()
    # return modified_at.date() == pd.to_datetime('2016-10-27').date()



def poll_washoe(url): 

    # todo: find a way to handle timeouts

    print 'requesting : ' + url
    r = requests.get(url, stream=True)
    print 'status     : {}'.format(r.status_code)

    return r.status_code == requests.codes.ok



if __name__ == "__main__":
    main()
