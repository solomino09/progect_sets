from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class Industry(models.Model):
    title = models.CharField(_("Title of Industry"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True, default="")

    class Meta:
        verbose_name_plural = "Industries"

    def __str__(self):
        return self.title


class Technology(models.Model):
    title = models.CharField(_("Title of Technology"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True, default="")

    class Meta:
        verbose_name_plural = "Technologies"

    def __str__(self):
        return self.title


class Company(models.Model):
    title = models.CharField(_("Title of Company"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True, default="")

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(_("Title of Project"), max_length=255, unique=True)
    url = models.TextField(_("URL"), max_length=255, blank=True, default="")
    notes = models.CharField(_("Notes"), max_length=255, blank=True, default="")
    date = models.DateField(_("Project readiness date"), null=True, blank=True)
    industries = models.ManyToManyField(
        Industry,
        related_name="industries",
        help_text="Select industries for this project",
    )
    technologies = models.ManyToManyField(
        Technology,
        related_name="technologies",
        help_text="Select technologies for this project",
    )
    description = models.TextField(_("Description"), blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        # editable=False,
        related_name="+",
        on_delete=models.SET_NULL,
    )

    def update_es_index(self, refresh=False, elasticsearch=None):

        if elasticsearch is None:
            from elasticsearch import Elasticsearch

            es = Elasticsearch(settings.ELASTICSEARCH_URLS)
        else:
            es = elasticsearch

        doc = {
            "created_by": self.created_by.id,
            "industries": list(x.pk for x in self.industries.all()),
            "technologies": list(x.pk for x in self.technologies.all()),
        }

        print("DOC - ", doc)
        index_name = "projects"
        res = es.index(
            index=index_name,
            doc_type="_doc",
            id=self.id,
            body=doc,
            # refresh='wait_for',
        )
        return res

    def __str__(self):
        return self.title


class ElasticSearchIndexInfo(models.Model):
    index_name = models.CharField(_("Index name"), max_length=120, unique=True)

    class Meta:
        verbose_name = _("ElasticSearch index info")
        verbose_name_plural = _("ElasticSearch indices info")
        ordering = ["id"]

    def __str__(self):
        return self.index_name
