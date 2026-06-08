from django.urls import path
from myapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('showdata/', views.showdata, name='showdata'),
    path('deletedata/<int:id>', views.deletedata, name='deletedata'),
    # path('update/<int:id>', views.updatedata, name='updatedata')
]
