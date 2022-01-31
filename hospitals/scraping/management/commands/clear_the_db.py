from django.core.management.base import BaseCommand
from django.db.models import Count
from scraping.models import *
from datetime import timedelta, datetime
from django.utils.timezone import utc
from hospitals_core.models import *
#from scrapping.tasks import *

def now():
	return datetime.utcnow().replace(tzinfo=utc)


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--daily_delete',
            help='Delete poll instead of closing it',
        )

    def handle(self, *args, **options):
            ScrapedHospitals.objects.all().delete()
            print("All data should be deleted")