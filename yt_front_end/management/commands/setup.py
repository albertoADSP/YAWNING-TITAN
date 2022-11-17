import shutil
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = 'sets up yawning titan dependencies'

    def handle(self, *args, **kwargs):
        print("Running setup...")
        from dir_setup import _create_app_dirs     
        from yawning_titan import DATA_DIR
        from yt_front_end import _YT_FRONT_ROOT_DIR
        _create_app_dirs()
        # Creates the static ui files copy in the data directory
        shutil.copytree(
            (_YT_FRONT_ROOT_DIR / "static").as_posix(), 
            DATA_DIR.as_posix(), 
            dirs_exist_ok=True
        )
