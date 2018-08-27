# -*- coding: utf-8 -*-

from scripts.SistrTyping import RunSistrWorkflow, CleanSistrWorkflow, UnlockSistrWorkflow
from cleo import Application

application = Application('stype_cli', '0.1.0')
application.add(RunSistrWorkflow())
application.add(CleanSistrWorkflow())
application.add(UnlockSistrWorkflow())

if __name__ == '__main__':
    application.run()