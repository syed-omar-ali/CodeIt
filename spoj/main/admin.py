from django.contrib import admin

# Register your models here.
from .models import Profile,Problem,Synced,Follow

admin.site.register(Profile)
admin.site.register(Problem)
admin.site.register(Synced)
admin.site.register(Follow)