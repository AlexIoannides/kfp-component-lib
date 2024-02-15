"""Developer task automation."""
import os

import nox

PYTHON = ["3.10"]

nox.options.sessions = [
    "check_code_formatting",
    "check_types",
    "run_tests",
]


@nox.session(python=PYTHON)
def run_tests(session: nox.Session):
    """Run unit tests."""
    session.install(".[dev]")
    pytest_args = session.posargs if session.posargs else []
    session.run("pytest", *pytest_args)


@nox.session(python=PYTHON, reuse_venv=True)
def format_code(session: nox.Session):
    """Lint code and re-format where necessary."""
    session.install(".[dev]")
    session.run("black", "--config=pyproject.toml", ".")
    session.run("ruff", "check", ".", "--config=pyproject.toml", "--fix")


@nox.session(python=PYTHON, reuse_venv=True)
def check_code_formatting(session: nox.Session):
    """Check code for formatting errors."""
    session.install(".[dev]")
    session.run("black", "--config=pyproject.toml", "--check", ".")
    session.run("ruff", "check", ".", "--config=pyproject.toml")


@nox.session(python=PYTHON, reuse_venv=True)
def check_types(session: nox.Session):
    """Run static type checking."""
    session.install(".[dev]")
    session.run("mypy", "src", "tests", "noxfile.py")


@nox.session(python=PYTHON, reuse_venv=True)
def build_and_deploy_pkg(session: nox.Session):
    """Build wheel and deploy to PyPI."""
    session.install(".[deploy]")
    session.run("rm", "-rf", "dist", external=True)
    session.run("python", "-m", "build")

    if session.posargs and session.posargs[0] != "deploy=false":
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ModuleNotFoundError:
            session.warn("Expecting PYPI_USR and PYPI_PWD in local env vars.")

        try:
            PYPI_USR = os.environ["PYPI_USR"]
            PYPI_PWD = os.environ["PYPI_PWD"]
        except KeyError as e:
            session.error(f"{str(e)} not found in local environment variables.")

        session.run("twine", "upload", "dist/*", "-u", PYPI_USR, "-p", PYPI_PWD)


@nox.session(python=PYTHON, reuse_venv=True)
def build_and_deploy_container_image(session: nox.Session):
    """Build container image and deploy to Docker Hub."""
    session.install(".")
    image_name = session.run(
        "python",
        "-c",
        "from kfp_component_lib import KFP_CONTAINER_IMAGE; print(KFP_CONTAINER_IMAGE, end='')",  # noqa
        silent=True,
    )
    image_name_str = str(image_name)
    session.run("docker", "build", "-t", image_name_str, ".", external=True)
    if session.posargs and session.posargs[0] != "deploy=false":
        session.run("docker", "image", "push", image_name_str, external=True)
