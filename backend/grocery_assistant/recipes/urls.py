from .views import RecipeViewSet, IngredientViewSet
from .views import TagViewSet
#from .create_my_fixtures import myload
from django.urls import path
from django.urls import include
from rest_framework import routers
'''


app_name = 'api'


router.register('titles', TitlesViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>[\d]+)/reviews',
    ReviewViewSet,
    basename='review'
)
router.register(
    r'titles/(?P<title_id>[\d]+)/reviews/(?P<review_id>[\d]+)/comments',
    CommentViewSet,
    basename='comments'
)
urlpatterns = [
    path('v1/', include(router.urls)),
]'''

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
'''router.register(
    r'tags/(?P<recipe_id>[\d]+)/',
    TagsViewSet,
    basename='tags'
)'''
router.register(r'tags',
    TagViewSet,
    basename='tags'
)
router.register(r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)


urlpatterns = [
    #path('download_data/', myload),
    path('', include(router.urls)),
]