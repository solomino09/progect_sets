from django.conf import settings
from typing import Optional
from collections import namedtuple


SLUG_SAVE_AS_DASH = ".,/"
SLUG_ALLOWED_CHARS = r"^[a-zA-Z0-9\-]$"


def slugify_unicode(value, save_as_dash=SLUG_SAVE_AS_DASH, dash="-"):
    import re
    import slugify

    for k in save_as_dash:
        value = value.replace(k, dash)
    result = slugify.slugify(value, only_ascii=True)

    pattern = re.compile(SLUG_ALLOWED_CHARS)
    result = "".join(filter(lambda x: pattern.match(x) is not None, result))
    return result


def get_unique_slug(
    value,
    model_class,
    slug_attr="slug",
    slug_func=slugify_unicode,
    ignore_slugs=[],
    query_init_expr=None,
):
    """ Generate unique slug for a model."""
    import itertools

    _slug = _orig = slug_func(value)
    for x in itertools.count(1):
        if query_init_expr:
            query = model_class.objects.filter(query_init_expr)
        else:
            query = model_class.objects.all()
        if (
            not query.exclude(**{"%s__in" % slug_attr: ignore_slugs})
            .filter(**{slug_attr: _slug})
            .exists()
        ):
            break
        _slug = "%s-%d" % (_orig, x)
    return _slug


def markdown_to_html(source):
    import markdown

    html = markdown.markdown(
        source,
        extensions=[
            "markdown.extensions.nl2br",
            # 'urlize',
        ],
    )
    return html


def send_mail(
    to=[],
    subject="",
    html_template="",
    txt_template="",
    context={},
    from_email=settings.DEFAULT_FROM_EMAIL,
):
    """Send mail to the all contacts
    """
    from django.core import mail
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string

    _to = to

    context.update(
        {"SITE_URL": settings.SITE_URL,}
    )

    text = render_to_string(txt_template, context)
    html = render_to_string(html_template, context)

    result = None

    with mail.get_connection() as connection:
        mail = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=from_email,
            to=_to,
            connection=connection,
        )
        mail.attach_alternative(html, "text/html")
        result = mail.send(fail_silently=True)
    return result


def flatten(d, parent_key="", sep="."):
    import collections

    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def send_email(request, form, user, template_name):
    from email.mime.text import MIMEText
    from django.contrib.auth.tokens import default_token_generator
    from django.contrib.sites.shortcuts import get_current_site
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
    from django.utils.encoding import force_bytes
    import os
    import smtplib

    current_site = get_current_site(request)
    msg = MIMEText(
        render_to_string(
            template_name,
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            },
        )
    )
    msg["Subject"] = "Activate your account changes."
    msg["From"] = os.environ.get("EMAIL_HOST_USER")
    msg["To"] = form.cleaned_data.get("email")
    s = smtplib.SMTP("smtp.mailgun.org", 587)
    s.login(os.environ.get("EMAIL_HOST_USER"), os.environ.get("EMAIL_HOST_PASSWORD"))
    s.sendmail(msg["From"], msg["To"], msg.as_string())
    s.quit()


def send_email_reset_password(request, form, user, template_name):
    from email.mime.text import MIMEText
    from django.contrib.auth.tokens import default_token_generator
    from django.contrib.sites.shortcuts import get_current_site
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
    from django.utils.encoding import force_bytes
    import os
    import smtplib

    current_site = get_current_site(request)
    msg = MIMEText(
        render_to_string(
            template_name,
            {
                "email": user.email,
                "user": user.name,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            },
        )
    )
    msg["Subject"] = "Reset password."
    msg["From"] = os.environ.get("EMAIL_HOST_USER")
    msg["To"] = form.cleaned_data.get("email")
    s = smtplib.SMTP("smtp.mailgun.org", 587)
    s.login(os.environ.get("EMAIL_HOST_USER"), os.environ.get("EMAIL_HOST_PASSWORD"))
    s.sendmail(msg["From"], msg["To"], msg.as_string())
    s.quit()
