from django.conf.urls import url
from CreateRule import views
# SET THE NAMESPACE!
app_name = 'CreateRule'
# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    url(r'^register/$', views.register, name='register'),
    url(r'^user_login/$', views.user_login, name='user_login'),
    url(r'^create_rule/$', views.create_rule, name='create_rule'),
    url(r'^see_rules/$', views.see_rules, name='see_rules'),
    url(r'^upload_file/$', views.upload_file, name='upload_file'),
    url(r'^edit/$', views.edit, name='edit'),
]