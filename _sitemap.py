import os
import sitemap
import ablog
from ablog.blog import Blog, os_path_join

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.join(PROJECT_ROOT, '_website')


def setup(app):
    """Setup ABlog extension."""

    app.connect('html-collect-pages', generate_sitemap)


def generate_sitemap(app):

    if not ablog.builder_support(app):
        return

    blog = Blog(app)

    base_url = blog.blog_baseurl
    if not base_url:
        raise StopIteration

    Sitemap(app=app, path=app.builder.outdir, base_url=base_url)
    if 0:
        # this is to make the function a generator
        # and make work for Sphinx 'html-collect-pages'
        yield


class Sitemap(sitemap.Sitemap):

    def __init__(self, app, *args, **kwargs):
        self._app = app
        self._blog = Blog(app)
        sitemap.Sitemap.__init__(self, *args, **kwargs)

    def list(self):
        for post in self._blog.posts:
            post_url = os_path_join(self._base_url, self._app.builder.get_target_uri(post.docname))
            if post.section:
                pass  # continue
            url = sitemap.Url(
                url=post_url,
                last_modified=(post.update or post.date).strftime("%Y-%m-%d"),
                change_frequency='weekly',
                priority='0.9'
            )
            yield url
