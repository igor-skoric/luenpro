from django.contrib import admin

from .models import Project, ProjectImage, ProjectTranslation


class ProjectTranslationInline(admin.TabularInline):
    model = ProjectTranslation
    extra = 1
    min_num = 1
    fields = ('language', 'title', 'description', 'status')


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'is_main', 'sort_order')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_display', 'is_published', 'sort_order', 'image_count')
    list_filter = ('is_published',)
    list_editable = ('is_published', 'sort_order')
    ordering = ('sort_order', 'id')
    inlines = [ProjectTranslationInline, ProjectImageInline]

    @admin.display(description='naziv')
    def title_display(self, obj):
        return obj.get_title()

    @admin.display(description='slike')
    def image_count(self, obj):
        return obj.images.count()
