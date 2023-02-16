import subprocess as cmd
import typer

app = typer.Typer()


@app.command()
def dev():
    cmd.run(f"python main.py", check=True, shell=True)


@app.command()
def format():
    cmd.run(f"black -q .", check=True, shell=True)


# FILE.ico: apply the icon to a Windows executable. FILE.exe,ID: extract the icon with ID from an
# exe. FILE.icns: apply the icon to the .app bundle on Mac OS. If an image file is entered that
# isn't in the platform format (ico on Windows, icns on Mac), PyInstaller tries to use Pillow to
# translate the icon into the correct format (if Pillow is installed). Use "NONE" to not apply any
# icon, thereby making the OS show some default (default: apply PyInstaller's icon). This option
# can be used multiple times.

# $python cli.py build -n app

# Read this and there are more you need to do to make this work
# https://stackoverflow.com/questions/62451711/pyinstaller-icon-option-doesnt-work-on-mac
# $python cli.py build app example.icns

# $python cli.py build app
@app.command()
def build(name: str):
    # def build(name: str, icofile: str):
    """
    main.spec, buid/main and dist/main executable file were created
    ./main or click it to test and use $ls -lh to see the file size.
    """

    cmd.run(f"pyinstaller main.py --onefile -n {name}", check=True, shell=True)
    # cmd.run(f"pyinstaller main.py --onefile -n {name} --windowed -i {icofile}", check=True, shell=True)


@app.command()
def requirements():
    cmd.run(f"pip freeze > requirements.txt", check=True, shell=True)


@app.command()
def install():
    cmd.run(f"pip install -r requirements.txt", check=True, shell=True)


if __name__ == "__main__":
    app()
