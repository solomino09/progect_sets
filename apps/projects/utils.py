def update_es_collection_index(elasticsearch=None):
    from elasticsearch import Elasticsearch
    from django.conf import settings
    from .models import Project

    # from apps.core.models import Language
    # from .models import ElasticSearchIndexInfo

    if elasticsearch is None:
        es = Elasticsearch(settings.ELASTICSEARCH_URLS)
    else:
        es = elasticsearch

    # print(filtered_properties, indexed_properties)
    # lang_codes = list(Language.objects.all().values_list('language', flat=True))

    index_name = "projects"

    # index_info = None
    # try:
    #     index_info = ElasticSearchIndexInfo.objects.get(index_name__exact=index_name)
    # except:
    #     index_info = ElasticSearchIndexInfo.objects.create(
    #         index_name=index_name)
    # print(index_name)
    _mapping = {
        "properties": {
            "created_by": {"type": "keyword"},
            "industries": {"type": "keyword"},
            "technologies": {"type": "keyword"},
        }
    }
    # print(_mapping)

    if es.indices.exists(index=index_name):
        # Delete index when mapping is changed.
        es.indices.delete(index=index_name)

    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={"mappings": _mapping})

    # if not index_info.mapping or index_info.mapping != _mapping:
    #     # Mapping has been changed or not set yet
    #     es.indices.close(index=index_name)
    #     es.indices.put_settings(index=index_name, body=_settings)
    #     es.indices.put_mapping(index=index_name, doc_type=type_doc, body=_mapping, include_type_name=True)
    #     es.indices.open(index=index_name)
    type_doc = "_doc"

    # es.indices.close(index=index_name)
    # # es.indices.put_settings(index=index_name, body=_settings)
    # es.indices.put_mapping(index=index_name, doc_type=type_doc, body=_mapping, include_type_name=True)
    # es.indices.open(index=index_name)

    # open_es_index_if_closed(index_name, elasticsearch=es)
    projects = Project.objects.all()
    for project in projects:
        project.update_es_index()

    es.indices.refresh(index=index_name)

    # index_info.mapping = _mapping
    # index_info.save()
