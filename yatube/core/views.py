from django.shortcuts import render


def page_not_found(request, exception):
    context = {
        'title': 'Ошибка 404'
    }
    return render(request, 'core/404.html', context, {'path': request.path},
                  status=404)


def csrf_failure(request, reason=''):
    context = {
        'title': 'Ошибка 403'
    }
    return render(request, 'core/403csrf.html', context)


def server_error(request, template_name='500.html'):
    context = {
        'title': 'Ошибка 500'
    }
    return render(request, template_name, context)
