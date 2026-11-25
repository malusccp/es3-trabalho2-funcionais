import json
import os
import pathlib
import urllib.error
import urllib.request

import pytest
from selenium import webdriver

FRONT_URL = os.getenv("FRONT_URL", "http://127.0.0.1:5173")
API_URL = os.getenv("API_URL", "http://127.0.0.1:5001")


@pytest.fixture
def front_url():
    return FRONT_URL


@pytest.fixture
def driver(request):
    opcoes = webdriver.ChromeOptions()
    if os.getenv("HEADLESS") == "1":
        opcoes.add_argument("--headless=new")
    opcoes.add_argument("--window-size=1280,1000")
    opcoes.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    drv = webdriver.Chrome(options=opcoes)
    drv.implicitly_wait(0)  # só esperas explícitas (WebDriverWait)
    yield drv
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        pasta = pathlib.Path("evidencias")
        pasta.mkdir(exist_ok=True)
        nome = request.node.name.replace("[", "_").replace("]", "")
        drv.save_screenshot(str(pasta / f"{nome}.png"))
    drv.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def servidor_zerado():
    req = urllib.request.Request(API_URL + "/api/admin/reset", data=b"{}", method="POST")
    urllib.request.urlopen(req)


@pytest.fixture
def estoque_pela_api():
    def _estoque(id_produto):
        return json.loads(urllib.request.urlopen(f"{API_URL}/api/produtos/{id_produto}").read())["stock"]
    return _estoque


@pytest.fixture
def status_do_pedido_pela_api():
    def _status(id_pedido):
        try:
            return urllib.request.urlopen(f"{API_URL}/api/pedidos/{id_pedido}").status
        except urllib.error.HTTPError as erro:
            return erro.code
    return _status
