r"""!
\file
\brief Various greetings
"""

from .. import add

def say_hello():
    """!The stock standard greeting."""
    print("Hello world!")

def say_hei():
    """!A nicer mathematical greeting."""
    print(f"Hei hei! add(1, 2) = {add(1, 2)}")
