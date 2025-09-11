"""
Herbie is your model output download assistant with a mind of his own.

██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██
  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██
██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██
  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██

                █ ██
                █ ██ ┏━┓ ┏━┓            ┏━┓   ┏━┓
                █ ██ ┃ ┃ ┃ ┃┏━━━━┓┏━┓┏━┓┃ ┃   ┏━┓┏━━━━┓
                █ ██ ┃ ┗━┛ ┃┃ ━━ ┃┃ ┏━━┛┃ ┗━━┓┃ ┃┃ ━━ ┃
                █ ██ ┃ ┏━┓ ┃┃ ━━━┓┃ ┃   ┃ ━━ ┃┃ ┃┃ ━━━┓
                █ ██ ┗━┛ ┗━┛┗━━━━┛┗━┛   ┗━━━━┛┗━┛┗━━━━┛
                █ ██
                       🏁 Retrieve NWP Model Data 🏁

██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██
  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██
██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██
  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██  ██

Herbie might look small on the outside, but he has a big heart on the
inside and will get you to the finish line. Happy racing! 🏁
"""

import os
from pathlib import Path

import toml

from herbie.misc import ANSI

__author__ = "Brian K. Blaylock"
__meet_Herbie__ = "https://en.wikipedia.org/wiki/Herbie"
__movie_clips__ = "https://youtube.com/playlist?list=PLrSOkJxBTv53gvwbw9pVlMm-1C2PUHJx7"
__Herbie_wins__ = "https://www.youtube.com/watch?v=4XWufUZ1mxQ&t=189s"
__documentation__ = "https://herbie.readthedocs.io/"


try:
    ## TODO: Will the `_version.py` file *always* be present?
    ## TODO: What if the person doesn't do "pip install"
    from ._version import __version__, __version_tuple__
except Exception:
    __version__ = "unknown"
    __version_tuple__ = (999, 999, 999)


########################################################################
# Overload Path object with my custom `expand` method so the user can
# set environment variables in the config file (e.g., ${HOME}).
def _expand(self, resolve: bool = False, absolute: bool = False) -> Path:
    """
    Fully expand the Path with the given environment variables.

    Optionally, resolve the path.

    Example
    -------
    >>> Path('$HOME').expand()
    Results in PosixPath('/p/home/blaylock')
    """
    p = Path(os.path.expandvars(self)).expanduser()

    if resolve:
        # TODO Why does this get stuck sometimes??
        p = p.resolve()

    if absolute:
        p = p.absolute()

    return p


Path.expand = _expand

########################################################################
# Location of Herbie's configuration file
_config_path = os.getenv("HERBIE_CONFIG_PATH", "~/.config/herbie")
_config_path = Path(_config_path).expand()
_config_file = _config_path / "config.toml"

# Default directory Herbie saves model output
# NOTE: The `\\` is an escape character in TOML.
#       For Windows paths, "C:\\user\\"" needs to be "C:\\\\user\\\\""
_save_dir = os.getenv("HERBIE_SAVE_DIR", "~/data")
_save_dir = Path(_save_dir).expand()
_save_dir = str(_save_dir).replace("\\", "\\\\")

# Default TOML Configuration Values
default_toml = f"""# Herbie defaults

[default]
model = "hrrr"
fxx = 0
save_dir = "{_save_dir}"
overwrite = false
verbose = true

# =============================================================================
# You can set the priority order for checking data sources.
# If you don't specify a default priority, Herbie will check each source in the
# order listed in the model template file. Beware: setting a default priority
# might prevent you from checking all available sources.
#
#priority = ['aws', 'nomads', 'google', 'etc.']

# =============================================================================
# Serverless configuration
# Set to true to prevent all file writes (for serverless/read-only environments)
# When enabled, Herbie will use temporary files and in-memory operations
#
#serverless = false

"""

# Default `custom_template.py` placeholder
default_custom_template = """
# ======================
# Private Model Template
# ======================
# Read more details at
# https://herbie.readthedocs.io/en/stable/user_guide/extend.html

# Uncomment and edit the class below, add additional classes, and edit
# the SOURCES dictionary to help Herbie locate your locally stored GRIB2
# files.

'''
class model1_name:
    def template(self):
        self.DESCRIPTION = "Local GRIB Files for model1"
        self.DETAILS = {
            "local_main": "These GRIB2 files are from a locally-stored modeling experiments."
            "local_alt": "These GRIB2 files are an alternative location for these model files."
        }

        # These PRODUCTS are optional but can provide an additional parameter to search for files.
        self.PRODUCTS = {
            "prs": "3D pressure level fields",
            "sfc": "Surface level fields",
        }

        # These are the paths to your local GRIB2 files.
        self.SOURCES = {
            "local_main": f"/path/to/your/model1/templated/with/{self.model}/gribfiles/{self.date:%Y%m%d%H}/nest{self.nest}/the_file.t{self.date:%H}z.{self.product}.f{self.fxx:02d}.grib2",
            "local_alt": f"/alternative/path/to/your/model1/templated/with/{self.model}/gribfiles/{self.date:%Y%m%d%H}/nest{self.nest}/the_file.t{self.date:%H}z.{self.product}.f{self.fxx:02d}.grib2",
        }
        self.LOCALFILE = f"{self.get_remoteFileName}"
'''
"""

########################################################################
# Check for serverless mode
# Auto-detect serverless environments or use explicit setting
def _detect_serverless_environment():
    """Detect if we're running in a serverless environment."""
    # Explicit setting takes precedence
    explicit_setting = os.getenv("HERBIE_SERVERLESS", "").lower()
    if explicit_setting in ["true", "1", "yes"]:
        return True
    if explicit_setting in ["false", "0", "no"]:
        return False
    
    # Auto-detect common serverless environments
    serverless_indicators = [
        "AWS_LAMBDA_FUNCTION_NAME",      # AWS Lambda
        "GOOGLE_CLOUD_PROJECT",          # Google Cloud Functions
        "AZURE_FUNCTIONS_WORKER_RUNTIME", # Azure Functions
        "VERCEL",                        # Vercel
        "NETLIFY",                       # Netlify
        "SCW_FUNCTION_NAME",             # Scaleway Functions
        "RAILWAY_ENVIRONMENT",           # Railway
        "RENDER",                        # Render
    ]
    
    # Check for read-only filesystem (common in containers/serverless)
    try:
        test_path = Path.home() / ".herbie_write_test"
        test_path.touch()
        test_path.unlink()
    except (OSError, PermissionError, FileNotFoundError):
        return True
    
    # Check environment variables
    return any(os.getenv(indicator) for indicator in serverless_indicators)

_serverless_mode = _detect_serverless_environment()

########################################################################
# Load config file (create one if needed)
def _load_or_create_config():
    """Safely load or create configuration, handling serverless environments."""
    if _serverless_mode:
        # In serverless mode, use default configuration without file operations
        config = toml.loads(default_toml)
        # Only print if verbose mode is enabled (check env var)
        if os.getenv("HERBIE_VERBOSE", "true").lower() not in ["false", "0", "no"]:
            print(f"Herbie: Running in serverless mode - using default config")
        return config
    
    # Try to load existing config file
    try:
        config = toml.load(_config_file)
        return config
    except FileNotFoundError:
        # Config file doesn't exist, try to create it
        pass
    except Exception as e:
        # Other errors loading config (permissions, corrupt file, etc.)
        if os.getenv("HERBIE_VERBOSE", "true").lower() not in ["false", "0", "no"]:
            print(f"Herbie: Warning - Could not load config file: {e}")
        return toml.loads(default_toml)
    
    # Attempt to create config file and directory
    try:
        _config_path.mkdir(parents=True, exist_ok=True)
        with open(_config_file, "w", encoding="utf-8") as f:
            f.write(default_toml)

        # Create `custom_template.py` placeholder
        _init_path = _config_path / "__init__.py"
        _custom_path = _config_path / "custom_template.py"
        if not _init_path.exists():
            with open(_init_path, "w") as f:
                pass
        if not _custom_path.exists():
            with open(_custom_path, "w") as f:
                f.write(default_custom_template)

        # Only print success message if verbose
        if os.getenv("HERBIE_VERBOSE", "true").lower() not in ["false", "0", "no"]:
            print(f"Herbie: Created config file at {_config_file}")

        # Load the newly created config file
        return toml.load(_config_file)
        
    except (OSError, PermissionError, IOError) as e:
        # Failed to create config file - fall back to defaults
        if os.getenv("HERBIE_VERBOSE", "true").lower() not in ["false", "0", "no"]:
            print(f"Herbie: Using default config (could not write to {_config_file})")
        return toml.loads(default_toml)

config = _load_or_create_config()


# Set serverless mode in config
config["default"]["serverless"] = _serverless_mode

# Expand the full path for `save_dir`
if _serverless_mode:
    # In serverless mode, use temp directory for any required file operations
    import tempfile
    config["default"]["save_dir"] = Path(tempfile.gettempdir()) / "herbie_temp"
else:
    config["default"]["save_dir"] = Path(config["default"]["save_dir"]).expand()

if os.getenv("HERBIE_SAVE_DIR") and not _serverless_mode:
    config["default"]["save_dir"] = Path(os.getenv("HERBIE_SAVE_DIR")).expand()
    # Only print if verbose mode is enabled
    if os.getenv("HERBIE_VERBOSE", "true").lower() not in ["false", "0", "no"]:
        print(f"Herbie: Using save_dir from HERBIE_SAVE_DIR: {os.getenv('HERBIE_SAVE_DIR')}")

from herbie.core import Herbie
from herbie.show_versions import show_versions
from herbie.fast import FastHerbie
from herbie.latest import HerbieLatest, HerbieWait
from herbie.wgrib2 import wgrib2
from herbie.accessors import HerbieAccessor
