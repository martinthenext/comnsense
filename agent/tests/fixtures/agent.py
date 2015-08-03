import allure
import pytest
import subprocess
import os


@pytest.yield_fixture(scope="session")
def agent_host():
    yield "127.0.0.1"


@pytest.yield_fixture(scope="session")
def agent_port():
    yield 55555


@pytest.yield_fixture()
def agent(agent_host, agent_port, tmpdir, request):
    connection = "tcp://%s:%d" % (agent_host, agent_port)
    log = tmpdir.join("comnsense-agent.log").strpath
    level = "DEBUG"
    path = request.config.rootdir.join("bin").join("comnsense-agent").strpath
    cmd = ["python", path, "-b", connection,
           "--log-level", level, "--log-filename", log]
    allure.attach("command", " ".join(cmd))
    proc = subprocess.Popen(cmd, close_fds=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    yield proc
    proc.terminate()
    out, err = proc.communicate()
    allure.attach("out", out)
    allure.attach("err", err)
    if os.path.exists(log):
        with open(log) as h:
            allure.attach("log", h.read())
