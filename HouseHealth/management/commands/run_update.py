from django.core.management.base import BaseCommand
from HouseHealth.view_utils import handle_UpdateAll
from Telescope.settings import logger


class Command(BaseCommand):
    """
    custom command to run mqtt client.
    """

    def handle(self, *args, **options):
        try:

            handle_UpdateAll()
        except Exception as e:
            logger.error("Exception in Updating data. Exception " + str(e))
