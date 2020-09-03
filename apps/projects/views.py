from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def projects(request):
    from .models import Project, Technology, Industry
    from elasticsearch import Elasticsearch

    es = Elasticsearch()
    user = request.user

    body_projects_from_es = {
        "query": {"terms": {"created_by": [user.id], "boost": 1.0}}
    }
    user_projects_from_es = es.search(index="projects", body=body_projects_from_es)
    user_projects = []
    for hit in user_projects_from_es["hits"]["hits"]:
        user_projects.append(Project.objects.get(pk=hit["_id"]))

    body_filter_from_es = {
        "aggs": {
            "created_by": {
                "terms": {"field": "created_by", "include": [user.id]},
                "aggs": {
                    "technologies": {
                        "terms": {
                            "field": "technologies",
                        }
                    },
                    "industries": {
                        "terms": {
                            "field": "industries",
                        }
                    },
                },
            }
        }
    }
    user_filter_from_es = es.search(index="projects", body=body_filter_from_es)
    user_technologies = []
    user_industries = []
    for buckets in user_filter_from_es["aggregations"]["created_by"]["buckets"]:
        for technology in buckets["technologies"]["buckets"]:
            user_technology = []
            user_technology.append(Technology.objects.get(pk=technology["key"]))
            user_technology.append(technology["doc_count"])
            user_technologies.append(user_technology)
        for industry in buckets["industries"]["buckets"]:
            user_industry = []
            user_industry.append(Industry.objects.get(pk=industry["key"]))
            user_industry.append(industry["doc_count"])
            user_industries.append(user_industry)
    context = {
        "user": user,
        "menu": "personal_information",
        "user_projects": user_projects,
        "user_technologies": user_technologies,
        "user_industries": user_industries,
    }
    return render(request, "projects.html", context)
