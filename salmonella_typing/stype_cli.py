# -*- coding: utf-8 -*-

from scripts.SistrTyping import SistrTyping
from cleo import Application

application = Application('stype_cli', '0.1.0')
application.add(SistrTyping())

if __name__ == '__main__':
    application.run()