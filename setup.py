from pathlib import Path
from setuptools import setup, find_packages

from setup import CMakeExtension, configure_command, predicate, \
    get_cmake_builder, version_from_git

PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT/"build"
TEST_DIR = PROJECT_ROOT/"tests"
CONFIG_FILE = BUILD_DIR/"configure.out.pkl"

@configure_command(CONFIG_FILE)
class Configure:
    catch = dict(help="path to catch", cmake="CATCH_INCLUDE",
                 check=predicate.directory)

setup(
    name="pycpp_build",
    version=version_from_git(plain=True),
    author="Jan-Lukas Wynen",
    author_email="j-l.wynen@hotmail.de",
    description="A hybrid Python/C++ test project",
    long_description="",
    # tell setuptools to look for any packages under "src"
    packages=find_packages("src"),
    # tell setuptools that all packages will be under the "src" directory
    # and nowhere else
    package_dir={"": "src"},
    # add an extension module named "pycpp_build" to the package
    # "pycpp_build"
    ext_modules=[CMakeExtension("pycpp_build/pycpp_build")],
    cmdclass={
        "configure": Configure,
        "build_ext": get_cmake_builder(CONFIG_FILE, TEST_DIR),
    },
    zip_safe=False,
    python_requires=">=3.6.5",
    entry_points={
        "console_scripts": ["hei = pycpp_build.scripts.main:main"]
    },
)
