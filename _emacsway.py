import os
from werkzeug.contrib.atom import format_iso8601
from werkzeug.http import http_date
from ablog.blog import Blog, urljoin, os_path_join, CONFIG

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.join(PROJECT_ROOT, '_website')

CONFIG_EXTRA = [
    ('canonical_baseurl', None, True),
]


def setup(app):
    """Setup ABlog extension."""
    for args in CONFIG_EXTRA:
        app.add_config_value(*args)
        CONFIG.append(args)

    app.connect('builder-inited', extend_template_engine)


def extend_template_engine(app):

    app.builder.templates.environment.filters['iso8601'] = format_iso8601
    app.builder.templates.environment.filters['http_date'] = http_date


def page_url(self, pagename):
    """Return page URL when :confval:`blog_baseurl` is set, otherwise
    ``None``. When found, :file:`index.html` is trimmed from the end
    of the URL."""

    if self.config['blog_baseurl']:
        url = pagename
        if url.endswith('index'):
            url = url[:-5]
        url = self.app.builder.get_target_uri(url)
        url = os_path_join(self.config['blog_baseurl'], url)
        return url


def canonical_url(self, pagename):
    """Return page URL when :confval:`blog_baseurl` is set, otherwise
    ``None``. When found, :file:`index.html` is trimmed from the end
    of the URL."""

    if self.config['canonical_baseurl']:
        url = pagename
        if url.endswith('index'):
            url = url[:-5]
        url = self.app.builder.get_target_uri(url)
        url = os_path_join(self.config['canonical_baseurl'], url)
        return url


Blog.page_url = page_url
Blog.canonical_url = canonical_url
