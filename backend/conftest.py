def pytest_addoption(parser):  # type: ignore
    parser.addoption(
        "--refresh-db",
        action="store",
        default="true",
        help="Refresh the test database before running tests (default: true).",
    )


def pytest_configure(config):  # type: ignore
    value = config.getoption("--refresh-db", default="true")
    refresh = str(value).lower() in ("true", "1", "yes")
    if hasattr(config.option, "reuse_db"):
        config.option.reuse_db = not refresh
    if hasattr(config.option, "create_db"):
        config.option.create_db = refresh
