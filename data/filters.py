import django_filters
from .models import Games, GameInfo, About
from django import forms

class GameFilter(django_filters.FilterSet):

    series = django_filters.CharFilter(field_name="series", lookup_expr="icontains")

    released_after = django_filters.DateFilter(
        field_name="release_date", lookup_expr="gte"
    )
    released_before = django_filters.DateFilter(
        field_name="release_date", lookup_expr="lte"
    )

    developer = django_filters.CharFilter(
        field_name="developer", lookup_expr="icontains"
    )

    publisher = django_filters.CharFilter(field_name="publisher", lookup_expr="exact")

    class Meta:
        model = Games
        fields = []


class InfoFilter(django_filters.FilterSet):
    game = django_filters.NumberFilter(field_name="game__id")
    game_name = django_filters.CharFilter(
        field_name="game__game_name", lookup_expr="icontains"
    )

    composer = django_filters.CharFilter(field_name="composer", lookup_expr="icontains")

    muliplayer = django_filters.BooleanFilter(
        field_name="multiplayer", lookup_expr="icontains"
    )

    class Meta:
        model = GameInfo
        fields = ["game", "game_name", "composer", "multiplayer"]


class AboutFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(
        method="filter_search",
        label="Search",
    )

    year = django_filters.NumberFilter(
        field_name="game__release_date__year",
        lookup_expr="exact",
        label="Year",
    )

    ordering = django_filters.OrderingFilter(
        fields=(
            ("game__game_name", "name"),
            ("game__release_date", "release_date"),
        ),
        field_labels={
            "name": "Name",
            "release_date": "Release Date",
        },
        label="Sort By",
        choices=(
            ("game__game_name", "A → Z"),
            ("-game__game_name", "Z → A"),
            ("-game__release_date", "Newest"),
            ("game__release_date", "Oldest"),
        ),
    )

    platform = django_filters.CharFilter(
        field_name="platform", lookup_expr="icontains"
    )

    genre = django_filters.CharFilter(
        field_name="genre", lookup_expr="icontains"
    )

    developer = django_filters.CharFilter(
        field_name="game__developer", lookup_expr="icontains"
    )

    publisher = django_filters.CharFilter(
        field_name="game__publisher", lookup_expr="icontains"
    )

    series = django_filters.CharFilter(
        field_name="game__series", lookup_expr="icontains"
    )

    steam_appid = django_filters.NumberFilter(
        field_name="steam_appid",
        lookup_expr="exact",
    )

    released_after = django_filters.DateFilter(
        field_name="game__release_date",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    released_before = django_filters.DateFilter(
        field_name="game__release_date",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = About
        fields = [
            "search",
            "year",
            "platform",
            "genre",
            "developer",
            "publisher",
            "series",
            "steam_appid",
            "released_after",
            "released_before",
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(game__game_name__icontains=value)
            | models.Q(game__series__icontains=value)
            | models.Q(game__developer__icontains=value)
            | models.Q(game__publisher__icontains=value)
            | models.Q(genre__icontains=value)
        )