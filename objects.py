'''
Created on 22/12/2015

@author: capi
'''

import logging


class ApiError(Exception):

    def __init__(self, errors, url=None):
        super(ApiError, self).__init__()
        self.errors = errors
        self.url = url

    def __str__(self):

        message = self.url or ''

        message = message + " -- "

        for e in self.errors:

            message = message + (" %d: %s," % (e['code'], e['message']))

        return message

class TwitterObject(object):

    BLOCKEABLE_ERRORS_CODES = [32,34,64,68,88,89,92,130,131,135,161,179,185,215,231,261, 326]

    def __init__(self, response, header=None, url=None):

        self.url = url
        self.is_error = False

#         try:
        if (header and header['status'] != '200') or (not isinstance(response, list) and response.get('errors')):
            self.is_error = True
            self.errors = response['errors']

        if not self.is_error:
            self.set_attributes(response, header)
        else:

            for er in self.errors:
                if er['code'] in self.BLOCKEABLE_ERRORS_CODES:
                    raise ApiError(self.errors, self.url)

            errors_str = str(self.errors)

            logging.debug("%s, for call %s" % (errors_str, self.url))


    def set_attributes(self, response, header):
        pass

#         except KeyError:
#             logging.error('Estructura inesperada')
#             logging.debug(response)
#             logging.debug(header)
#         except TypeError as e:
#             logging.error('Tipo de Objeto inesperado')
#             logging.info(response)
#             logging.info(header)
#             logging.info(str(e))
#         except AttributeError:
#             logging.error('No se recibio un response')
#             logging.debug(response)
#             logging.debug(header)


    def get(self, key):

        return self.dict[key]

class User(TwitterObject):


    def set_attributes(self, dict, header):

        self.id = dict.get('id')
        self.name = dict['name']
        self.screen_name = dict['screen_name']

        # if received as user
        self.following = dict.get('following')
        self.description = dict.get('description')
        self.lang = dict.get('lang')
        self.profile_image_url = dict.get('profile_image_url')
        self.followers_count = dict.get('followers_count')
        self.profile_banner_url = dict.get('profile_banner_url')

        # if received as friendship
        self.connections = dict.get('connections')

    def get_url(self):
        return ('http://twitter.com/%s' % self.screen_name)

    def is_friend(self):

        if self.connections:
            return 'following' in self.connections and 'followed_by' in self.connections

    @classmethod
    def from_users(cls, users_raw, header):

        users = []

        for obj in users_raw:
            users.append(User(obj, header))

        return users

class UsersList(TwitterObject):

    def set_attributes(self, response, header):

        self.users = []

        for obj in response:
            self.users.append(User(obj, header))



class Tweet(TwitterObject):

    def set_attributes(self, dict, header):

        self.id = dict.get('id')
        self.text = dict['text']
        self.user = User(dict['user'], header)
        self.favorited = dict['favorited']
        self.retweeted = dict['retweeted']
        self.lang = dict['lang']

    def get_url(self):

        if not self.is_error:

            return "https://twitter.com/%s/status/%d" % (self.user.screen_name, self.id)
        else:
            return None

class TweetsList(TwitterObject):
    tweets = []

    def set_attributes(self, response, header):

        if isinstance(response, list):
            statuses = response
        else:
            statuses = response['statuses']

        self.tweets = []

        for s in statuses:

            self.tweets.append(Tweet(s, header ))


class Friendship(TwitterObject):

    def __init__(self, attr, header=None):
        super(Friendship, self).__init__(attr, header)

        if not self.is_error:

            self.dict = attr['relationship']

            self.target = self.dict['target']
            self.source = self.dict['source']

    def are_friends(self):

        return self.target['following'] and self.target['followed_by']
