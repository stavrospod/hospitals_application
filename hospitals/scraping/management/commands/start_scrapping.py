from django.core.management.base import BaseCommand
from django.db.models import Count
from datetime import timedelta, datetime
from django.utils.timezone import utc
from scraping.tasks import *

def now():
	return datetime.utcnow().replace(tzinfo=utc)


class Command(BaseCommand):
	help = 'Displays stats related to Article and Comment models'

	def handle(self, *args, **kwargs):
		print("DATA HAS BEEN ADDED")