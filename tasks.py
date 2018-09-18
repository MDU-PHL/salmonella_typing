'''
Automate the build of the container and validation.
This uses invoke

To run:
inv build_container

Find out what tasks are available:
inv --list
'''

from invoke import task

@task
def clean(c):
    print("Removing container")
    c.sudo("rm -rf salmonella_typing.simg")

@task(clean)
def build_container(c):
    print("Building container")
    c.sudo('singularity build salmonella_typing.simg Singularity')

@task(build_container)
def run_validation(c):
    print("Generating validation data")
    c.run("./salmonella_typing.simg validate")