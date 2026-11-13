import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ums-super-secret-key-cse601330-2026')
    
    # SQLite Database Configuration (Zero Configuration / Password-Free)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(basedir, "ums.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session & Cookie Security (Rubric: Forms, Validation, Cookies & Sessions)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    REMEMBER_COOKIE_DURATION = 86400 * 7  # 7 days
    REMEMBER_COOKIE_HTTPONLY = True

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "ums_test.db")}'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
