from django.views.generic.base import TemplateView


class AboutTechViews(TemplateView):
    template_name = 'about/tech.html'


class AboutAuthorViews(TemplateView):
    template_name = 'about/author.html'
