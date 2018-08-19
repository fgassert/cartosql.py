'''
Carto-python bindings
'''

from carto.auth import APIKeyAuthClient
from carto.datasets import DatasetManager
from . import CARTO_KEY, CARTO_USER, CARTO_URL


def setProperties(datasetName, properties, user=None, key=None):
    '''
    Update a carto Dataset with new properties
    '''
    key = key or CARTO_KEY
    user = user or CARTO_USER
    url = CARTO_URL.format(user)
    auth = APIKeyAuthClient(url, key)
    manager = DatasetManager(auth)
    dataset = manager.get(datasetName)
    dataset.update_from_dict(properties)
    dataset.save()
    return dataset.__dict__

def getProperties(datasetName, user=None, key=None):
    key = key or CARTO_KEY
    user = user or CARTO_USER
    url = CARTO_URL.format(user)
    auth = APIKeyAuthClient(url, key)
    manager = DatasetManager(auth)
    return manager.get(datasetName).__dict__

def setPrivacy(datasetName, privacy, user=None, key=None):
    '''
    Set dataset privacy (LINK, PUBLIC, PRIVATE)
    '''
    if privacy.upper() not in ['LINK', 'PUBLIC', 'PRIVATE']:
        raise(Exception('Privacy must be one of "LINK", "PUBLIC", "PRIVATE"'))
    return setProperties(datasetName, {'privacy': privacy}, user, key)['privacy']
