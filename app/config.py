import os


class BaseConfig(object):

    """
    Configuration base, for all environments.
    """

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                             'postgresql://postgres:postgres@localhost:5432/server_list')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get('DEBUG', 'True')
    SECRET_KEY = 'wer234r6amsfdyustyi65e9eiwhy794ol421tgs00768ny576w4q'
    CSRF_ENABLED = True


class ProductionConfig(BaseConfig):
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEVELOPMENT = True
    DEBUG = True
