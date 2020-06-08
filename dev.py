import logging
import sys
import app

IS_DEV = False
if __name__ == '__main__':
    IS_DEV = True

app.init(debug=IS_DEV)

from app.functions.dashboard import *
# from app.functions.test_logging import *

if IS_DEV:
    from flask import Flask, request
    app = Flask(__name__)

    '''
    @app.route('/', methods=['POST', 'GET'])
    def test():
        return test_message(request)
    '''

    functions = ['dashboard']
    # app.add_url_rule('/dashboard', dashboard, locals()[dashboard], methods=['POST', 'GET'], defaults={'request': request})
    for function in functions:
        app.add_url_rule(f'/{function}', function, locals()[function], methods=['POST', 'GET'], defaults={'request': request})

    app.run(host='127.0.0.1', port=8088, debug=True, passthrough_errors=True)