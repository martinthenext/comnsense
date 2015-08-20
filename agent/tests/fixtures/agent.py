import allure
import copy
import json
import os
import pytest
import random
import subprocess
import time

from .network import host, port


@pytest.yield_fixture()
def agent(host, port, tmpdir, request):
    connection = "tcp://%s:%d" % (host, port)
    log = tmpdir.join("comnsense-agent.log").strpath
    level = "DEBUG"
    path = request.config.rootdir.join("bin").join("comnsense-agent").strpath
    cmd = ["python", path, "-b", connection,
           "--log-level", level, "--log-filename", log]

    with allure.step("start agent: %s" % connection):
        allure.attach("command", " ".join(cmd))
        env = dict(copy.deepcopy(os.environ).iteritems())
        allure.attach("env", json.dumps(env, indent=2))
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        allure.attach("pid", str(proc.pid))

    time.sleep(1)  # wait for python

    yield proc

    if proc.poll() is None:
        proc.terminate()
    out, err = proc.communicate()
    allure.attach("out", out)
    allure.attach("err", err)

    if os.path.exists(log):
        with open(log) as h:
            allure.attach("log", h.read())
