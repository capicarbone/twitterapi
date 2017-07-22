'''
Created on 21/12/2015

@author: capi
'''

import httplib2
import json
import logging
import time
import urllib

import oauth2 as oauth
from objects import *


class TwitterClientBase(object):
    '''
    classdocs
    '''

    def _get_params(self):

        return {
                  'oauth_version': "1.0",
                  'oauth_nonce': oauth.generate_nonce(),
                  'oauth_timestamp': str(int(time.time())),
                  'oauth_token': self.token.key,
                  'oauth_consumer_key': self.consumer.key
        }

    def _sign_request(self, request):

        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        request.sign_request(signature_method, self.consumer, self.token)

        return request


    def __init__(self, consumer_data, token_data):

        self.consumer = oauth.Consumer(
                                       key=consumer_data['KEY'],
                                       secret=consumer_data['SECRET'])

        self.token = oauth.Token(
                                 key=token_data['KEY'],
                                 secret=token_data['SECRET'])

    def utf8encode_params(self, params):

        if params:
            for key in params.keys():

                if isinstance(params[key], basestring):

                    params[key] = params[key].encode('utf8')

            return params

    def make_request(self, url_base, method, url_params=None, encoded_params=None):

        body = ''
        url = url_base
        parameters = self._get_params()

        if url_params:
            url_params = self.utf8encode_params(url_params)
            url = url + "?" + urllib.urlencode(url_params)

        if encoded_params:
            encoded_params = self.utf8encode_params(encoded_params)
            body = urllib.urlencode(encoded_params)
            parameters.update(encoded_params)

        # TODO: If development enviroment
        #logging.info('Request to Twitter API ' + url)

        request = oauth.Request(method=method, url=url, parameters=parameters, body=body)
        if encoded_params:
            request.is_form_encoded = True

        self._sign_request(request)

        header, content = httplib2.Http().request(url, method=method, body=body,
            headers=request.to_header())

        try:
            response = json.loads(content)
        except ValueError:
            logging.error("No hay formato JSON")
            logging.debug('Request to Twitter API ' + url)
            logging.debug(content)
            response = {}

        return response, header

    def ids_to_str(self, array):
        '''
            @param array: Array of integer ids
            @return: string of list of ids comma-separated
        '''

        str_ids = ''

        for id in array:
            str_ids = str_ids + ( ",%d" % (id) )

        return str_ids[1:]



class TwitterRESTClient(TwitterClientBase):

    def get_user_timeline(self, **kwargs):
        ''' This method is only for test
        '''

        url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        method = "GET"

        return self.make_request(url, method, kwargs)

    def get_user(self, id, **kwargs):

        url = 'https://api.twitter.com/1.1/users/show.json'
        method = 'GET'

        kwargs['user_id'] = id

        response, header = self.make_request(url, method, kwargs)

        return User(response, header, url)



    def follow(self, id, **kwargs):

        url = 'https://api.twitter.com/1.1/friendships/create.json'
        method = 'POST'

        kwargs['id'] = id

        response, header = self.make_request(url, method, kwargs)

        return User(response, header, url)

        '''
            si following es falso, no se seguia a la cuenta anteriormente, si es true ya se seguia.
        '''

    def mute(self, id, **kwargs):

        url = 'https://api.twitter.com/1.1/mutes/users/create.json'
        method = 'POST'

        kwargs['id'] = id

        response, header = self.make_request(url, method, kwargs)

        return User(response, header, url)

    def unmute(self, id, **kwargs):

        url = 'https://api.twitter.com/1.1/mutes/users/destroy.json'
        method = 'POST'

        kwargs['id'] = id

        response, header = self.make_request(url, method, kwargs)

        return User(response, header, url)

    def unfollow(self, **kwargs):

        url = 'https://api.twitter.com/1.1/friendships/destroy.json'
        method = 'POST'

        response, header = self.make_request(url, method, kwargs)

        return User(response, header, url)

    def like(self, id, **kwargs):

        url = 'https://api.twitter.com/1.1/favorites/create.json'
        method = 'POST'

        kwargs['id'] = id

        response, header = self.make_request(url, method, kwargs)

        return Tweet(response, header, url)

    def unlike(self, id, **kwargs):

        url = 'https://api.twitter.com/1.1/favorites/destroy.json'
        method = 'POST'

        kwargs['id'] = id

        response, header = self.make_request(url, method, kwargs)

        return Tweet(response, header, url)



    def search_tweets(self, query, **kwargs):

        url = 'https://api.twitter.com/1.1/search/tweets.json'
        method = 'GET'

        kwargs['q'] = query

        response, header = self.make_request(url, method, kwargs)

        return TweetsList(response, header, url)

    def statuses_lookup(self, ids, **kwargs):
        '''
            @param ids: Array of integer tweet ids
        '''

        url = 'https://api.twitter.com/1.1/statuses/lookup.json'
        method = 'POST'

        kwargs['id'] = self.ids_to_str(ids)

        response, header = self.make_request(url, method, encoded_params=kwargs)

        return TweetsList(response, header, url)

    def get_friendship(self, **kwargs):

        url = 'https://api.twitter.com/1.1/friendships/show.json'
        method = 'GET'

        response, header = self.make_request(url, method, kwargs)

        return Friendship(response, header, url)

    def get_friendships(self, user_id, **kwargs):

        url = 'https://api.twitter.com/1.1/friendships/lookup.json'
        method = 'GET'

        kwargs['user_id'] = self.ids_to_str(user_id)

        response, header = self.make_request(url, method, kwargs)

        return UsersList(response, header, url)














