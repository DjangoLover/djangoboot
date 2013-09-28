from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView

from boots.models import Boot, BootVersion
from accounts.views import GroupMixin


class SearchView(TemplateView):
    template_name = 'boots/search.html'


class TrendingView(TemplateView):
    template_name = 'boots/trending.html'


class GroupView(TemplateView):
    template_name = 'boots/group.html'


class BootView(TemplateView):
    template_name = 'boots/boot.html'


class BootCreateView(GroupMixin, CreateView):
    model = Boot


class BootUpdateView(GroupMixin, UpdateView):
    model = Boot


class BootDeleteView(GroupMixin, DeleteView):
    model = Boot


class VersionView(TemplateView):
    template_name = 'boots/version.html'