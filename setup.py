import os
import re
import sys
import sysconfig
import platform
import subprocess
from pathlib import Path
import pickle

from shutil import copyfile, copymode
from distutils.version import LooseVersion
from distutils.cmd import Command
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

def parse_shell_command(cmd):
    if not cmd:
        return None

    status, output = subprocess.getstatusoutput(f"which {cmd}")
    if status == 0:
        return cmd
    print(f"Error: cannot execute command {cmd}:")
    print(f"  {output}")
    sys.exit(1)

def parse_file(fname):
    if not fname:
        return None

    path = Path(fname)
    if path.exists():
        return path.resolve()
    print(f"Error: path '{path}' does not exist")
    sys.exit(1)


class ConfigureCommand(Command):
    description = "configure build of C++ extension"
    user_options = [
        ("compiler=", None, "C++ compiler to use"),
        ("catch=", None, "path to catch"),
        ("build-type=", None, "CMake build type"),
    ]

    def initialize_options(self):
        """Set default values"""
        self.compiler = ""  # use default compiler
        self.catch = ""  # search in system path
        self.build_type = "devel"

    def finalize_options(self):
        """Post-process options"""

        self.compiler = parse_shell_command(self.compiler)
        self.catch = parse_file(self.catch)
        self.build_type = self.build_type.upper()
        if self.build_type not in ("DEVEL", "DEBUG", "RELEASE"):
            print(f"Error: build type not supported: {self.build_type}")
            sys.exit(1)

    def run(self):
        BUILD_DIR.mkdir(exist_ok=True)
        pickle.dump({"CMAKE_CXX_COMPILER": self.compiler,
                     "CMAKE_BUILD_TYPE": self.build_type,
                     "CATCH_INCLUDE": self.catch,
                    },
                    open(str(CONFIG_FILE), "wb"))


def common_cmake_args(config):
    return [f"-D{key}={val}" for key, val in config.items() if val] \
        + [f"-DPYTHON_EXECUTABLE={sys.executable}",
           f"-DPYTHON_CONFIG={sys.executable}-config",
           f"-DTEST_DIR={TEST_DIR}"]


class BuildExtension(build_ext):
    def run(self):
        # make sure that cmake is installed
        _ = parse_shell_command("cmake")

        # read configuration file and prepare arguments for cmake
        try:
            config = pickle.load(open(str(CONFIG_FILE), "rb"))
        except FileNotFoundError:
            print("error: Configuration file not found. Did you forget to run the configure command first?")
            sys.exit(2)
        config_time = CONFIG_FILE.stat().st_mtime
        cmake_args = common_cmake_args(config)

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
            # call cmake
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
            ext_build_dir.rmdir()

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
        
class CatchTestCommand(TestCommand):
    "Execute Python and C++ Catch tests"

    def distutils_dir_name(self, dname):
        """Returns the name of a distutils build directory"""
        dir_name = "{dirname}.{platform}-{version[0]}.{version[1]}"
        return dir_name.format(dirname=dname,
                               platform=sysconfig.get_platform(),
                               version=sys.version_info)

    def run(self):
        # Run catch tests
        subprocess.call(["./*_test"],
                        cwd=os.path.join("build",
                                         self.distutils_dir_name("temp")),
                        shell=True)
        # Run Python tests
        super(CatchTestCommand, self).run()
        print("\nPython tests complete, now running C++ tests...\n")

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
        "configure": ConfigureCommand,
        "build_ext": BuildExtension,
    },
    zip_safe=False,
    python_requires=">=3.6.5",
    entry_points={
        "console_scripts": ["hei = pycpp_build.main:main"]
    },
    install_requires=["numpy>=1.14.3"],
)
