from werkzeug.wrappers import Request, Response
import json

@Request.application
def application(request):
    return Response(json.dumps(request.cookies))

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 80, application)
