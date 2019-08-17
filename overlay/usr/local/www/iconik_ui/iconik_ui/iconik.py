import os
import re
import urllib.parse
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect

from jinja2 import Environment, FileSystemLoader


CONFIG_FILE_PATH = '/usr/local/cantemo/iconik_storage_gateway/config.ini'


def get_hostname(url):
    return urllib.parse.urlparse(url).netloc


class IconikApp(object):

    credential_keys = ['app-id', 'auth-token', 'storage-id']

    def __init__(self):
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path), autoescape=True)
        self.jinja_env.filters['hostname'] = get_hostname

        self.url_map = Map([
            Rule('/', endpoint='index'),
            Rule('/update_credentials', endpoint='update_credentials'),
            Rule('/credential_success', endpoint='credential_success'),
        ])

    def on_index(self, request):
        config = self.get_config_contents()
        keys_present = len(list(filter(
            lambda v: v and v[0],
            map(
                lambda key: re.findall(fr'{key}.*=[\t ]*(.*)', config),
                self.credential_keys
            )
        ))) == 3
        return self.render_template('index.html', credentials_exist=keys_present)

    def get_config_contents(self):
        with open(CONFIG_FILE_PATH, 'r') as f:
            return f.read()

    def update_config_contents(self, data):
        with open(CONFIG_FILE_PATH, 'w') as f:
            f.write(data)

    def on_credential_success(self, request):
        return self.render_template('credential_success.html')

    def on_update_credentials(self, request):
        if request.method == 'POST':
            config = self.get_config_contents()
            for key, value in {k: request.form[k.replace('-', '_')] for k in self.credential_keys}.items():
                config = re.sub(
                    fr'({key}.*)=[\t ]*(.*)',
                    fr'\1= {value}',
                    config
                )

            self.update_config_contents(config)
            return redirect('credential_success')

        else:
            return self.error_404()

    def error_404(self):
        response = self.render_template('404.html')
        response.status_code = 404
        return response

    def render_template(self, template_name, **context):
        template = self.jinja_env.get_template(template_name)
        return Response(template.render(context), mimetype='text/html')

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except NotFound:
            return self.error_404()
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    app = IconikApp()
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/static': os.path.join(os.path.dirname(__file__), 'static')
    })
    run_simple('127.0.0.1', 8000, app, use_debugger=True, use_reloader=True)
