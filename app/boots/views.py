from django.views.generic import CreateView, UpdateView, DeleteView, View
from django.views.generic.edit import SingleObjectMixin, ModelFormMixin
from django.views.generic.detail import BaseDetailView
from django.views.generic.base import TemplateResponseMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from boots.models import Boot, BootVersion, Star
from boots.forms import BootVersionCreationForm
from accounts.views import TeamMixin, TeamObjectMixin
from boots.models import Team, Boot, BootVersion
from core.views import EnsureCSRFMixin, JSONResponseMixin
from haystack.views import SearchView as BaseSearchView


class BootObjectMixin(SingleObjectMixin):
    model = Boot
    context_object_name = 'boot'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        try:
            obj = queryset.get(team__slug=self.kwargs.get('team'),
                               slug=self.kwargs.get('boot'))
        except ObjectDoesNotExist:
            raise Http404

        self.boot = obj

        return obj


class BootVersionObjectMixin(SingleObjectMixin):
    model = BootVersion
    context_object_name = 'version'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        try:
            obj = queryset.get(boot__team__slug=self.kwargs.get('team'),
                               boot__slug=self.kwargs.get('boot'),
                               slug=self.kwargs.get('version'))
        except ObjectDoesNotExist:
            raise Http404

        self.boot = obj.boot

        return obj


from haystack.forms import SearchForm as BaseSearchForm
from haystack.query import SearchQuerySet
from boots.search_indexes import BootIndex

class SearchForm(BaseSearchForm):
    pass


class SearchView(BaseSearchView):
    template = 'boots/search.html'
    form = SearchForm
    results = SearchQuerySet().all()
    results_per_page = 1

    @classmethod
    def as_view(cls):
        return cls()


class TrendingView(SearchView):
    template_name = 'boots/trending.html'


class TeamView(TeamObjectMixin, SearchView):
    template_name = 'boots/team.html'

    def get_queryset(self):
        return super(TeamView, self).get_queryset().filter(team=self.object)


class BootContextMixin(object):

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(BootContextMixin, self).get_context_data(**kwargs)
        context['boot'] = self.boot
        context['team_member'] = user.get_teams().filter(id=self.boot.team.id) if user.is_authenticated() else False
        return context


class BootView(EnsureCSRFMixin, BootContextMixin, BootObjectMixin, TemplateResponseMixin, BaseDetailView):
    template_name = 'boots/boot.html'
    context_object_name = 'version'

    def get_object(self, queryset=None):
        super(BootView, self).get_object(queryset)
        try:
            return self.boot.versions.latest()
        except ObjectDoesNotExist:
            return None


class BootCreateView(TeamMixin, CreateView):
    model = Boot
    template_name = 'boots/boot_create.html'

    def get_initial(self):
        return {
            'team': self.request.user.team.id
        }


class BootUpdateView(TeamMixin, BootObjectMixin, UpdateView):
    template_name = 'boots/boot_update.html'


class BootDeleteView(TeamMixin, BootObjectMixin, DeleteView):
    template_name = 'boots/boot_delete.html'


class BootVersionCreateView(TeamMixin, BootObjectMixin, CreateView):
    template_name = 'boots/boot_version_create.html'
    form_class = BootVersionCreationForm
    model = BootVersion

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.boot = self.boot
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)


class BootVersionDeleteView(TeamMixin, BootVersionObjectMixin, DeleteView):
    template_name = 'boots/boot_version_delete.html'


class BootVersionView(EnsureCSRFMixin, BootContextMixin, BootVersionObjectMixin, TemplateResponseMixin, BaseDetailView):
    template_name = 'boots/boot.html'


class StarBootView(JSONResponseMixin, EnsureCSRFMixin, View):

    def json_post(self, request, *args, **kwargs):
        user = request.user

        response = {}

        if user.is_authenticated():
            boot_id = request.POST.get('boot_id')
            try:
                boot = Boot.objects.get(id=boot_id)
            except ObjectDoesNotExist:
                boot = None
                response['message'] = _('Boot not found.')

            if boot:
                value = request.POST.get('value') == 'true'
                try:
                    star = Star.objects.get(user=user, boot=boot)
                except Star.DoesNotExist:
                    star = None

                if not value:
                    if not star:
                        Star.objects.create(user=user, boot=boot)
                    response['value'] = True
                    response['message'] = _('Thank you!')
                else:
                    if star:
                        star.delete()
                    response['value'] = False

                response['count'] = Boot.objects.get(id=boot_id).star_count
        else:
            response['message'] = _('Must be logged in.')

        return response
