import os
import re
import sys
import sysconfig
import subprocess
from pathlib import Path
import pickle
import inspect
import shutil

import distutils.cmd
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.command.test import test as TestCommand

PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT/"build"
TEST_DIR = PROJECT_ROOT/"tests"
CONFIG_FILE = BUILD_DIR/"configure.out.pkl"

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

def is_executable(cmd):
    "Check if cmd is an executable command."
    status, output = subprocess.getstatusoutput(f"which {cmd}")
    if status == 0:
        return True
    print(f"error: Cannot execute command {cmd}:")
    print(f"  {output}")
    return False

def file_exists(fname):
    "Check if a file (or directory) exists."
    exists = Path(fname).exists()
    if not exists:
        print(f"error: File does not exist: {fname}")
    return exists

BUILD_TYPES = ("DEVEL", "RELEASE", "DEBUG")
DEFAULT_OPT_ARGS = dict(short_name=None, help="", bool=False, default=None, check=None)
DEFAULT_OPTIONS = dict(compiler={**DEFAULT_OPT_ARGS,
                                 "help": "C++ compiler",
                                 "cmake": "CMAKE_CXX_COMPILER",
                                 "long_name": "compiler=",
                                 "check": is_executable},
                       build_type={**DEFAULT_OPT_ARGS,
                                   "help": f"CMake build type, allowed values are {BUILD_TYPES}",
                                   "cmake": "CMAKE_BUILD_TYPE",
                                   "long_name": "build_type=",
                                   "default": "DEVEL",
                                   "check": lambda x: x in BUILD_TYPES})
FORBIDDEN_OPTIONS = ("description", "user_options")


def _parse_option(name, args):
    "Parse a single user option."
    # make sure everything is ok
    if name in FORBIDDEN_OPTIONS:
        print("error: Illegal option name for configure command: '{name}'")
        sys.exit(1)
    if name in DEFAULT_OPTIONS:
        print("warning: Option to configure command will be overwritten by default: '{compiler}'")
    if "cmake" not in args:
        print("error: No key 'cmake' in arguments for configure option '{name}'")
        sys.exit(1)

    # incorporate default arguments
    args = {**DEFAULT_OPT_ARGS, **args}
    if "long_name" not in args:  # add long_name if not given
        args["long_name"] = name + ("=" if not args["bool"] else "")
    # default for bools must be False, otherwise False could not be specified
    if args["bool"]:
        args["default"] = False
    return args

def _get_options(cls):
    "Extract user options from a class."
    underscore_re = re.compile("^_.*_$")
    options = {name: _parse_option(name, args)
               for name, args in inspect.getmembers(cls, lambda x: not inspect.isroutine(x))
               if not underscore_re.match(name)}
    return {**options, **DEFAULT_OPTIONS}

def _format_option(name, val):
    "Format name, value pair of user options."
    if val is None:
        val = "<unspecified>"
    return "{} = {}".format(name.split("=", 1)[0], val)

def configure_command(outfile):
    """
    Decorator for a distutils configure command class.
    Arguments:
       - outfile: Path to the output file.
    """

    def _wrap(cls):
        class _Configure(distutils.cmd.Command):
            description = "configure build of C++ extensions"
            # store full metadata on options
            options = _get_options(cls)
            # handled by distutils
            user_options = [(args["long_name"].replace("_", "-"), args["short_name"],
                             args["help"])
                            for _, args in options.items()]

            def initialize_options(self):
                "Set defaults for all user options."
                for name, args in self.options.items():
                    setattr(self, name, args["default"])

            def finalize_options(self):
                "Post process and verify user options."
                for name, args in self.options.items():
                    if args["bool"]:
                        setattr(self, name, str(bool(getattr(self, name))).upper())

                    check = args["check"]
                    val = getattr(self, name)
                    if check is not None and val is not None and not check(val):
                        print(f"Invalid argument to option {name}: '{getattr(self, name)}'")
                        sys.exit(1)

            def run(self):
                "Execute the command, writes configure file."
                print("-- " +
                      "\n-- ".join(_format_option(args["long_name"], getattr(self, name))
                                   for name, args in self.options.items()))
                print(f"writing configuration to file {outfile}")
                self.mkpath(str(Path(outfile).parent))
                pickle.dump({args["cmake"]: getattr(self, name)
                             for name, args in self.options.items()},
                            open(str(outfile), "wb"))

        return _Configure
    return _wrap

@configure_command(CONFIG_FILE)
class Configure:
    catch = dict(help="path to catch", cmake="CATCH_INCLUDE",
                 check=file_exists)
    foo = dict(bool=True, cmake="FOO")


def _common_cmake_args(config):
    "Format arguments for CMake common to all extensions."
    return [f"-D{key}={val}" for key, val in config.items() if val is not None] \
        + [f"-DPYTHON_EXECUTABLE={sys.executable}",
           f"-DPYTHON_CONFIG={sys.executable}-config",
           f"-DTEST_DIR={TEST_DIR}"]


class BuildExtension(build_ext):
    def run(self):
        # make sure that cmake is installed
        is_executable("cmake")

        # read configuration file and prepare arguments for cmake
        try:
            config = pickle.load(open(str(CONFIG_FILE), "rb"))
        except FileNotFoundError:
            print("error: Configuration file not found. Did you forget "
                  "to run the configure command first?")
            sys.exit(2)
        config_time = CONFIG_FILE.stat().st_mtime
        cmake_args = _common_cmake_args(config)

        # build all extensions
        for ext in self.extensions:
            self._build_extension(ext, cmake_args, config_time)

    def _run_cmake(self, extension, libname, ext_build_dir, cmake_args):
        print("running cmake")

        # where the extension library has to be placed (during build, not installation)
        extdir = Path(self.get_ext_fullpath(extension.name)).parent.resolve()
        # finalize arguments for cmake
        cmake_args = cmake_args \
                     + [f"-DLIBRARY_NAME={libname}",
                        f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}"]

        try:
            # call cmake from ext_build_dir
            subprocess.check_call(["cmake", extension.sourcedir] + cmake_args,
                                  cwd=ext_build_dir)
        except subprocess.CalledProcessError as err:
            print(f"Calling cmake failed with arguments {err.cmd}")
            sys.exit(1)

    def _build_extension(self, extension, cmake_args, config_time):
        print(f"building extension {extension.name}")

        # name of the output library
        libname = extension.name.rsplit("/", 1)[1]
        # directory to build the extension in
        ext_build_dir = Path(self.build_temp).resolve()/libname

        # configure was run after making the directory => start over
        if ext_build_dir.exists() and ext_build_dir.stat().st_mtime < config_time:
            shutil.rmtree(str(ext_build_dir))

        # need to run CMake
        if not ext_build_dir.exists():
            ext_build_dir.mkdir(parents=True)
            self._run_cmake(extension, libname, ext_build_dir, cmake_args)

        print("compiling extension")
        build_cmd = ["cmake", "--build", "."]
        if self.parallel:
            build_cmd += ["--", "-j", str(self.parallel)]
        try:
            subprocess.check_call(build_cmd, cwd=ext_build_dir)
            subprocess.check_call(["cmake", "--build", ".", "--target", "install"],
                                  cwd=ext_build_dir)
        except subprocess.CalledProcessError as err:
            print(f"Calling cmake to build failed, arguments {err.cmd}")
            sys.exit(1)

setup(
    name="pycpp_build",
    version="0.1",
    author="Jan-Lukas Wynen",
    author_email="j-l.wynen@hotmail.de",
    description="A hybrid Python/C++ test project",
    long_description="",
    # tell setuptools to look for any packages under "src"
    packages=find_packages("src"),
    # tell setuptools that all packages will be under the "src" directory
    # and nowhere else
    package_dir={"":"src"},
    # add an extension module named "pycpp_build" to the package
    # "pycpp_build"
    ext_modules=[CMakeExtension("pycpp_build/pycpp_build")],
    cmdclass={
        "configure": Configure,
        "build_ext": BuildExtension,
    },
    zip_safe=False,
    python_requires=">=3.6.5",
    entry_points={
        "console_scripts": ["hei = pycpp_build.main:main"]
    },
    install_requires=["numpy>=1.14.3"],
)
