import django_filters
from .models import Games , GameInfo , About


class GameFilter(django_filters.FilterSet):

    series = django_filters.CharFilter(
        field_name="series", lookup_expr="icontains"
    )

    released_after = django_filters.DateFilter(
        field_name="release_date", lookup_expr="gte"
    )
    released_before = django_filters.DateFilter(
        field_name="release_date", lookup_expr="lte"
    )

    developer = django_filters.CharFilter(
        field_name="developer" , lookup_expr="icontains"
    )

    publisher = django_filters.CharFilter(
        field_name="publisher" , lookup_expr="exact"
    )

    class Meta:
        model = Games
        fields = []

class InfoFilter(django_filters.FilterSet):
    game = django_filters.NumberFilter(
        field_name="game__id"
    )
    game_name = django_filters.CharFilter(
        field_name="game__game_name" , lookup_expr="icontains"
    )
    company = django_filters.CharFilter(
        field_name="game__company" , lookup_expr="icontains"
    )

    class Meta:
        model = GameInfo
        fields = ["game", "game_name", "company"]



class AboutFilter(django_filters.FilterSet):

    game = django_filters.NumberFilter(
        field_name="game__id"
    )

    game_name = django_filters.CharFilter(
        field_name="game__game_name",
        lookup_expr="icontains"
    )

    series = django_filters.CharFilter(
        field_name="game__series",
        lookup_expr="icontains"
    )

    company = django_filters.CharFilter(
        field_name="game__company",
        lookup_expr="icontains"
    )

    steam_appid = django_filters.CharFilter(
        field_name="steam_appid",
        lookup_expr="exact"
    )

    platforms = django_filters.CharFilter(
        field_name="platform",
        lookup_expr="icontains"
    )

    class Meta:
        model = About
        fields = ["game", "game_name", "series" , "company", "steam_appid" , "platforms"]