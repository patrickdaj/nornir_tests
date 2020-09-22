from nox.sessions import Session
import nox
import tempfile


def install_with_constraints(session: Session, *args: str, **kwargs: str) -> None:
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session(python=["3.6", "3.7", "3.8"])
def tests(session: Session) -> None:
    args = session.posargs
    session.run("poetry", "install", external=True)
    install_with_constraints(session, "pytest")
    session.run("pytest")


@nox.session(python="3.8")
def black(session: Session) -> None:
    args = session.posargs
    install_with_constraints(session, "black")
    session.run("black", "--check", ".")


@nox.session(python="3.8")
def mypy(session: Session) -> None:
    args = session.posargs
    install_with_constraints(session, "mypy")
    session.run("mypy", ".")


@nox.session(python="3.8")
def pylama(session: Session) -> None:
    args = session.posargs
    install_with_constraints(session, "pylama")
    session.run("pylama")
