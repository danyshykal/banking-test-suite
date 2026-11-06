import threading

import pytest
from werkzeug.serving import make_server

from app.bank_app import RELEASES, create_app
from tests.bank_client import BankClient


def pytest_addoption(parser):
    parser.addoption("--release", default="1.2", choices=sorted(RELEASES),
                     help="Which release of the bank app to test (default: 1.2, the latest)")


def _version(text):
    return tuple(int(part) for part in text.split("."))


@pytest.fixture(scope="session")
def release(request):
    return request.config.getoption("--release")


@pytest.fixture(scope="session")
def base_url(release):
    """Start the requested release of the bank API on a free port, once per run."""
    server = make_server("127.0.0.1", 0, create_app(release))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.fixture
def bank(base_url):
    return BankClient(base_url)


@pytest.fixture(autouse=True)
def _skip_features_not_in_release(request, release):
    """@pytest.mark.since("1.1") = this feature only exists from release 1.1 onwards."""
    marker = request.node.get_closest_marker("since")
    if marker and _version(release) < _version(marker.args[0]):
        pytest.skip(f"feature added in release {marker.args[0]}, testing {release}")
