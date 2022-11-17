def _create_app_dirs():
    """
    Handles creation of application directories and user directories.

    Uses `platformdirs.PlatformDirs` and `pathlib.Path` to create the required app directories in the correct
    locations based on the users OS.
    """
    import sys
    from pathlib import Path, PosixPath
    from typing import Final, Union

    from platformdirs import PlatformDirs

    _YT_PLATFORM_DIRS: Final[PlatformDirs] = PlatformDirs(
        appname="yawning_titan", appauthor="DSTL"
    )
    """An instance of `PlatformDirs` set with appname='yawning_titan' and appauthor='DSTL'."""

    app_dirs = [_YT_PLATFORM_DIRS.user_data_path]
    if sys.platform == "win32":
        app_dirs.append(_YT_PLATFORM_DIRS.user_data_path / "config")
        app_dirs.append(_YT_PLATFORM_DIRS.user_data_path / "logs")
        _YT_USER_DIRS: Final[Union[Path, PosixPath]] = (
            Path.home() / "DSTL" / "yawning_titan"
        )
    else:
        app_dirs.append(_YT_PLATFORM_DIRS.user_config_path)
        app_dirs.append(_YT_PLATFORM_DIRS.user_log_path)
        _YT_USER_DIRS: Final[Union[Path, PosixPath]] = Path.home() / "yawning_titan"

    app_dirs.append(_YT_PLATFORM_DIRS.user_data_path / "docs")
    app_dirs.append(_YT_PLATFORM_DIRS.user_data_path / "db")
    app_dirs.append(_YT_PLATFORM_DIRS.user_data_path / "app_images")
    app_dirs.append(_YT_USER_DIRS / "notebooks")
    app_dirs.append(_YT_USER_DIRS / "game_modes")
    app_dirs.append(_YT_USER_DIRS / "images")
    app_dirs.append(_YT_USER_DIRS / "agents")

    for app_dir in app_dirs:
        app_dir.mkdir(parents=True, exist_ok=True)