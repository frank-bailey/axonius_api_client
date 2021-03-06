@ECHO OFF
SET PATH=%PATH%;C:\Program Files\Python38;C:\Program Files\Python38\scripts

FOR /F "tokens=* USEBACKQ" %%F IN (`python get_version.py`) do (
    SET VERSION=%%F
)

if "%1" == "" goto help

if "%1" == "init" (
    :init
    echo.Initializing...
    call :pip_install_tools
    call :pip_install_dev
    call :pip_install
)

if "%1" == "help" (
    :help
    echo.Please use `make ^<target^>` where ^<target^> is one of
    echo.   init        to get things going
    echo.   test        run the test suite
    goto end
)

if "%1" == "pip_install_tools" (
    :pip_install_tools
    python -m pip install --quiet --upgrade --requirement requirements-pkg.txt
    echo.Packaging requirements installed
    goto end
)

if "%1" == "pip_install_dev" (
    :pip_install_dev
    python -m pip install --quiet --upgrade --requirement requirements-dev.txt
    echo.Developement requirements installed
    goto end
)

if "%1" == "pip_install" (
    :pip_install
    python -m pip install --quiet --upgrade --requirement requirements.txt
    echo.Package requirements installed
    goto end
)

if "%1" == "test" (
    :test
    pytest -ra --verbose --showlocals  --exitfirst axonius_api_client/tests --last-failed
    goto end
)

:end
