#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scripts.SistrTyping import (
    RunSistrWorkflow,
    CleanSistrWorkflow
    
)
# from scripts.SistrParse import ParseSistrOutput
# from validation.limitOfDetection.LODExperimentWorkflow import LODCommand
from cleo import Application

application = Application("stype_cli", "0.2.0")
application.add(RunSistrWorkflow())
application.add(CleanSistrWorkflow())
# application.add(LODCommand())

if __name__ == "__main__":
    application.run()
