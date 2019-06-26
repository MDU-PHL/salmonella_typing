#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scripts.SistrTyping import RunSistrWorkflow, CleanSistrWorkflow, UnlockSistrWorkflow
from scripts.SistrParse import ParseSistrOuput
from validation.limitOfDetection.LODExperimentWorkflow import LODCommand
from cleo import Application

application = Application('stype_cli', '0.1.0')
application.add(RunSistrWorkflow())
application.add(CleanSistrWorkflow())
application.add(UnlockSistrWorkflow())
application.add(ParseSistrOuput())
#application.add(LODCommand())

if __name__ == '__main__':
    application.run()