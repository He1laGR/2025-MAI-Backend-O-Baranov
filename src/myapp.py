from dotenv import load_dotenv
import os

load_dotenv() 

PROJECT_ROOT = os.getenv('PROJECT_ROOT')
PUBLIC_DIR = os.path.join(PROJECT_ROOT, 'public')


def app(environ, start_response):
    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']
    query = environ.get('QUERY_STRING', '')
    params = dict(param.split('=') for param in query.split('&') if '=' in param)
    headers = [('Content-type', 'text/html; charset=utf-8')]

    if path == '/':
        start_response('200 OK', headers)
        index_path = os.path.join(PUBLIC_DIR, 'index.html')
        with open(index_path, 'rb') as file:
            return [file.read()]
    
    elif path == '/about':
        start_response('200 OK', headers)
        return ['<h1>О нас</h1><p>Тут раздел с описанием сайта</p>'.encode('utf-8')]
    
    else:
        start_response('404 Not Found', headers)
        return ['<h1>404</h1><p>Страница не найдена</p>'.encode('utf-8')]

