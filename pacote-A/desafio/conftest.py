import json
import os
import pathlib
import urllib.request

import pytest
from selenium import webdriver

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def driver(request):
    opcoes = webdriver.ChromeOptions()
    if os.getenv("HEADLESS") == "1":
        opcoes.add_argument("--headless=new")
    opcoes.add_argument("--window-size=1280,900")
    # desliga o pop-up de senha do Chrome (inclusive o aviso de senha vazada/comum,
    # que aparece ~1 s depois do login e rouba o clique)
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
def sistema_zerado(base_url):
    req = urllib.request.Request(base_url + "/api/admin/reset", data=b"{}", method="POST")
    urllib.request.urlopen(req)


@pytest.fixture
def matricular_pela_api(base_url):
    def _matricular(aluno, disciplinas):
        corpo = json.dumps({"aluno": aluno, "disciplinas": disciplinas}).encode()
        req = urllib.request.Request(base_url + "/api/matriculas", data=corpo, method="POST",
                                     headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req).read())
    return _matricular
