# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-23 09:38
from __future__ import unicode_literals

from bulk_update.helper import bulk_update
from django.db import migrations
from pontoon.base.templatetags.helpers import as_simple_translation


def simplify_ftl_tm_entries(apps, schema):
    """
    Reformat all FTL source strings and translations in TranslationMemoryEntry
    table with as_simple_translation().

    See bug 1576120 for more details.
    """
    TranslationMemoryEntry = apps.get_model('base', 'TranslationMemoryEntry')

    tm_entries = (
        TranslationMemoryEntry.objects
        .filter(entity__resource__format='ftl')
    )

    for tme in tm_entries:
        tme.source = as_simple_translation(tme.source)
        tme.target = as_simple_translation(tme.target)

    bulk_update(
        tm_entries,
        update_fields=['source', 'target'],
        batch_size=1000,
    )


def revert_simplify_ftl_tm_entries(apps, schema):
    TranslationMemoryEntry = apps.get_model('base', 'TranslationMemoryEntry')

    tm_entries = (
        TranslationMemoryEntry.objects
        .filter(entity__resource__format='ftl')
        .prefetch_related('entity', 'translation')
    )

    for tme in tm_entries:
        tme.source = tme.translation.string
        tme.target = tme.entity.string

    bulk_update(
        tm_entries,
        update_fields=['source', 'target'],
        batch_size=1000,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0141_userprofile_use_translate_next'),
    ]

    operations = [
        migrations.RunPython(
            simplify_ftl_tm_entries,
            revert_simplify_ftl_tm_entries,
        )
    ]
