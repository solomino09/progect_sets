from django.contrib import admin
from .models import Industry, Technology, Project, Company
from import_export import widgets, fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ManyToManyWidget, IntegerWidget
import tablib


class CharRequiredWidget(widgets.CharWidget):
    def clean(self, value, row=None, *args, **kwargs):
        val = super().clean(value)
        if val:
            return val
        else:
            raise ValueError("this field is required")


class ForeignkeyRequiredWidget(widgets.ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            print(self.field, value)
            return self.get_queryset(value, row, *args, **kwargs).get(
                **{self.field: value}
            )
        else:
            raise ValueError(self.field + " required")


class IndustryAdmin(admin.ModelAdmin):
    list_display = ("title",)


admin.site.register(Industry, IndustryAdmin)


class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("title",)


admin.site.register(Technology, TechnologyAdmin)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ("title",)


admin.site.register(Company, CompanyAdmin)


class ProjectResource(resources.ModelResource):
    # id = fields.Field(
    #     column_name="id",
    #     attribute="id",
    #     saves_null_values=False,
    #     widget=IntegerWidget(),
    # )
    title = fields.Field(
        column_name="title",
        attribute="title",
        saves_null_values=False,
        widget=CharRequiredWidget(),
    )
    # url = fields.Field(
    #     column_name="url",
    #     attribute="url",
    #     saves_null_values=False,
    #     widget=CharRequiredWidget(),
    # )
    industries = fields.Field(
        column_name="industries",
        attribute="industries",
        widget=ManyToManyWidget(Industry, field="title"),
    )
    technologies = fields.Field(
        column_name="technologies",
        attribute="technologies",
        widget=ManyToManyWidget(Technology, field="title"),
    )

    class Meta:
        model = Project
        fields = (
            "title",
            "url",
            "industries",
            "technologies",
            "description",
            "notes",
        )
        import_id_fields = ("title",)
        export_order = (
            "title",
            "url",
            "industries",
            "technologies",
            "description",
            "notes",
        )
        export_id_fields = ("title",)
        skip_unchanged = True

    def before_import_row(self, row, **kwargs):
        value_industries = row["industries"]
        for i in value_industries.split(","):
            formated_industries_row = []
            if not Industry.objects.filter(title__iexact=i):
                obj_industry = Industry.objects.create(title=i.capitalize())
                formated_industries_row.append(i.capitalize())
            else:
                formated_industries_row.append(i.capitalize())
            row["industries"] = ",".join(formated_industries_row)

        value_technologies = row["technologies"]
        for i in value_technologies.split(","):
            formated_technologies_row = []
            if not Technology.objects.filter(title__iexact=i):
                obj_technology = Technology.objects.create(title=i.capitalize())
                formated_technologies_row.append(i.capitalize())
            else:
                formated_technologies_row.append(i.capitalize())
            row["technologies"] = ",".join(formated_technologies_row)
        # Project.objects.filter(created_by=kwargs['user']).filter(title=row['title']).delete()

    def after_import_instance(self, instance, new, **kwargs):
        instance.created_by = kwargs["user"]


class ProjectAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ProjectResource
    list_display = ("title", "created_by")


admin.site.register(Project, ProjectAdmin)
