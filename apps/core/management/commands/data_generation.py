from django.core.management.base import BaseCommand, CommandError
from faker import Faker
import random

FAKE = Faker()

INDUSTRIES_LIST = [
    "Legal",
    "Real Estate",
    "Big Data",
    "Consulting",
    "Freelance",
    "Matching platform",
    "Social Network",
    "Data and Analytics",
    "Productivity Tools",
    "Real Time",
    "Task Management",
    "Test and Measurement",
]

TECHNOLOGIES_LIST = [
    "Java",
    "Kotlin",
    "Swift",
    "Objective-C",
    "С++",
    "C#",
    "PHP",
    "Ruby",
    "Python",
    "NodeJS",
    "Perl",
    "Go",
    "JavaScript",
]

NUMBER_OF_PROJECTS = 40


def create_industries():
    from apps.projects.models import Industry

    industries = Industry.objects.all()

    for industry in INDUSTRIES_LIST:
        if not industries.filter(title=industry):
            industries.create(title=industry)


def create_technologies():
    from apps.projects.models import Technology

    technologies = Technology.objects.all()

    for technology in TECHNOLOGIES_LIST:
        if not technologies.filter(title=technology):
            technologies.create(title=technology)


def create_projects(amount_of_projects):
    from apps.projects.models import Company, Project

    projects = Project.objects.all()

    i = 0
    while i < amount_of_projects:
        project_title = FAKE.cryptocurrency_name()
        if not projects.filter(title=project_title):
            projects.create(
                title=project_title,
                url=FAKE.dga(),
                date=FAKE.date_this_century(),
                # company=companies[i],
                description=FAKE.paragraph(),
            )
            i += 1


def fill_in_projects():
    from apps.projects.models import Industry, Project, Technology

    projects = Project.objects.all()

    for project in projects:
        for i in range(5):
            project.industries.add(Industry.objects.get(title=INDUSTRIES_LIST[i]))

        for i in range(5):
            project.technologies.add(Technology.objects.get(title=TECHNOLOGIES_LIST[i]))

        project.save()


class Command(BaseCommand):
    args = ""
    help = "START GENERATION DATA"

    def handle(self, *args, **options):
        create_industries()
        create_technologies()
        create_projects(NUMBER_OF_PROJECTS)
        fill_in_projects()
