from fabric.api import local, task

@task
def compile_scss():
    # Currently just a single file - no need to walk directories.
    local("pyscss --output=app/static/css/main.css --no-compress "
          "app/static/css/scss/main.scss")
