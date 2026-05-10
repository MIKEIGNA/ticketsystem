from celery import shared_task
from django.core.management import call_command


@shared_task
def sync_kpl_thesportsdb_incremental():
    call_command("sync_thesportsdb_kpl", mode="incremental")


@shared_task
def sync_kpl_thesportsdb_full():
    call_command("sync_thesportsdb_kpl", mode="full")
