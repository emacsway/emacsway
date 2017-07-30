import os
import time
import datetime
import ablog
from werkzeug.contrib.atom import format_iso8601
from werkzeug.http import http_date
from ablog.blog import Blog, os_path_join

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.join(PROJECT_ROOT, '_website')


def setup(app):
    """Setup ABlog extension."""
    app.connect('builder-inited', extend_template_engine)


def extend_template_engine(app):
    app.builder.templates.environment.filters['iso8601'] = format_iso8601
    app.builder.templates.environment.filters['http_date'] = http_date
