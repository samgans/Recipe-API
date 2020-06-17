from rest_framework import filters


class IsOwnerFilterBackend(filters.BaseFilterBackend):
    '''Filters objects which were created by the request user'''
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(owner=request.user)


class RecipeTagsFilterBackend(filters.BaseFilterBackend):
    '''Filters recipes by the tags'''
    def filter_queryset(self, request, queryset, view):
        tags_str = request.query_params.get('tags')
        if tags_str:
            list_tags = [int(i) for i in tags_str.split(',')]
            return queryset.filter(tags__id__in=list_tags)
        return queryset


class RecipeIngredientsFilterBackend(filters.BaseFilterBackend):
    '''Filters recipes by the ingredients'''
    def filter_queryset(self, request, queryset, view):
        ingr_str = request.query_params.get('ingredients')
        if ingr_str:
            list_ingrs = [int(i) for i in ingr_str.split(',')]
            return queryset.filter(ingredients__id__in=list_ingrs)
        return queryset


class AssignedToRecipeFilterBackend(filters.BaseFilterBackend):
    '''
    Filters tag or ingredient by the fact that it assigned or not to a recipe
    '''
    def filter_queryset(self, request, queryset, view):
        assigned = (request.query_params.get('assigned') == '1')
        not_assigned = (request.query_params.get('not_assigned') == '1')

        if assigned:
            return queryset.filter(recipe__isnull=False).distinct()
        elif not_assigned:
            return queryset.filter(recipe__isnull=True).distinct()
        return queryset
