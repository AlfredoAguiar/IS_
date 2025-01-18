from django.urls import path
from .views.file_views import FileUploadView, FileUploadChunksView, GetAllCarsView, GetCarsByMakeModelView, GetCarsByPriceRangeView, GetCarsByYearConditionView
from .views.file_views_weather import FileUploadView as WeatherFileUploadView
from .views.file_views_weather import FileUploadChunksView as WeatherFileUploadChunksView
from .views.file_views import GetCarByVinView, UpdateCarView, DeleteCarView, GetAllCarsView_2
from .views.file_views_weather import GetWeatherByLocationView, GetWeatherByDateRangeView, GetWeatherByRegionView

urlpatterns = [
    # File Upload Views
    path('upload-file/', FileUploadView.as_view(), name='upload_file'),
    path('upload-file/by-chunks', FileUploadChunksView.as_view(), name='upload-file-by-chunks'),

    # Car Views
    path('cars/all/', GetAllCarsView.as_view(), name='get_all_cars'),
    path('cars/make-model/', GetCarsByMakeModelView.as_view(), name='get_cars_by_make_model'),
    path('cars/price-range/', GetCarsByPriceRangeView.as_view(), name='get_cars_by_price_range'),
    path('cars/year-condition/', GetCarsByYearConditionView.as_view(), name='get_cars_by_year_condition'),

    # Weather Views
    path('weather/region/', GetWeatherByRegionView.as_view(), name='get_weather_by_region'),
    path('weather/location/', GetWeatherByLocationView.as_view(), name='get_weather_by_location'),
    path('weather/date-range/', GetWeatherByDateRangeView.as_view(), name='get_weather_by_date_range'),

    # Weather File Upload Views
    path('weather/upload-file/', WeatherFileUploadView.as_view(), name='weather_upload_file'),
    path('weather/upload-file/by-chunks', WeatherFileUploadChunksView.as_view(), name='weather_upload_file_by_chunks'),

    path('cars/all_2/', GetAllCarsView_2.as_view(), name='get_all_cars_2'),
    path('cars/get-car-by-vin/', GetCarByVinView.as_view(), name='get-car-by-vin'),
    path('cars/update-car/', UpdateCarView.as_view(), name='update-car'),
    path('cars/delete-car/', DeleteCarView.as_view(), name='delete-car'),

]