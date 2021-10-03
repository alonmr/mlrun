import pytest

import mlrun
from mlrun.serving import GraphContext
from mlrun.utils import logger

from .demo_states import *  # noqa

try:
    import storey
except Exception:
    pass

engines = [
    "sync",
    "async",
]


def myfunc1(x, context=None):
    assert isinstance(context, GraphContext), "didnt get a valid context"
    return x * 2


def myfunc2(x):
    return x * 2


class Mul(storey.MapClass):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def do(self, event):
        return event * 2


def test_basic_flow():
    fn = mlrun.new_function("tests", kind="serving")
    graph = fn.set_topology("flow", engine="sync")
    graph.add_step(name="s1", class_name="Chain")
    graph.add_step(name="s2", class_name="Chain", after="$prev")
    graph.add_step(name="s3", class_name="Chain", after="$prev")

    server = fn.to_mock_server()
    # graph.plot("flow.png")
    print("\nFlow1:\n", graph.to_yaml())
    resp = server.test(body=[])
    assert resp == ["s1", "s2", "s3"], "flow1 result is incorrect"

    graph = fn.set_topology("flow", exist_ok=True, engine="sync")
    graph.add_step(name="s2", class_name="Chain")
    graph.add_step(
        name="s1", class_name="Chain", before="s2"
    )  # should place s1 first and s2 after it
    graph.add_step(name="s3", class_name="Chain", after="s2")

    server = fn.to_mock_server()
    logger.info(f"flow: {graph.to_yaml()}")
    resp = server.test(body=[])
    assert resp == ["s1", "s2", "s3"], "flow2 result is incorrect"

    graph = fn.set_topology("flow", exist_ok=True, engine="sync")
    graph.add_step(name="s1", class_name="Chain")
    graph.add_step(name="s3", class_name="Chain", after="$prev")
    graph.add_step(name="s2", class_name="Chain", after="s1", before="s3")

    server = fn.to_mock_server()
    logger.info(f"flow: {graph.to_yaml()}")
    resp = server.test(body=[])
    assert resp == ["s1", "s2", "s3"], "flow3 result is incorrect"


@pytest.mark.parametrize("engine", engines)
def test_handler(engine):
    fn = mlrun.new_function("tests", kind="serving")
    graph = fn.set_topology("flow", engine=engine)
    graph.to(name="s1", handler="(event + 1)").to(name="s2", handler="json.dumps")
    if engine == "async":
        graph["s2"].respond()

    server = fn.to_mock_server()
    resp = server.test(body=5)
    if engine == "async":
        server.wait_for_completion()
    # the json.dumps converts the 6 to "6" (string)
    assert resp == "6", f"got unexpected result {resp}"


def test_handler_with_context():
    fn = mlrun.new_function("tests", kind="serving")
    graph = fn.set_topology("flow", engine="sync")
    graph.to(name="s1", handler=myfunc1).to(name="s2", handler=myfunc2).to(
        name="s3", handler=myfunc1
    )
    server = fn.to_mock_server()
    resp = server.test(body=5)
    # expext 5 * 2 * 2 * 2 = 40
    assert resp == 40, f"got unexpected result {resp}"


def test_init_class():
    fn = mlrun.new_function("tests", kind="serving")
    graph = fn.set_topology("flow", engine="sync")
    graph.to(name="s1", class_name="Echo").to(name="s2", class_name="RespName")

    server = fn.to_mock_server()
    resp = server.test(body=5)
    assert resp == [5, "s2"], f"got unexpected result {resp}"


def test_on_error():
    fn = mlrun.new_function("tests", kind="serving")
    graph = fn.set_topology("flow", engine="sync")
    graph.add_step(name="s1", class_name="Chain")
    graph.add_step(name="raiser", class_name="Raiser", after="$prev").error_handler(
        "catch"
    )
    graph.add_step(name="s3", class_name="Chain", after="$prev")
    graph.add_step(name="catch", class_name="EchoError").full_event = True

    server = fn.to_mock_server()
    logger.info(f"flow: {graph.to_yaml()}")
    resp = server.test(body=[])
    assert resp["error"] and resp["origin_state"] == "raiser", "error wasnt caught"


def return_type(event):
    return event.__class__.__name__


def test_content_type():
    fn = mlrun.new_function("tests", kind="serving")
    graph = fn.set_topology("flow", engine="sync")
    graph.to(name="totype", handler=return_type)
    server = fn.to_mock_server()

    # test that we json.load() when the content type is json
    resp = server.test(body={"a": 1})
    assert resp == "dict", "invalid type"
    resp = server.test(body="[1,2]")
    assert resp == "list", "did not load json on no type"
    resp = server.test(body={"a": 1}, content_type="application/json")
    assert resp == "dict", "invalid type, should keep dict"
    resp = server.test(body="[1,2]", content_type="application/json")
    assert resp == "list", "did not load json"
    resp = server.test(body="[1,2]", content_type="application/text")
    assert resp == "str", "did not keep as string"
    resp = server.test(body="xx [1,2]")
    assert resp == "str", "did not keep as string"
    resp = server.test(body="xx [1,2]", content_type="application/json", silent=True)
    assert resp.status_code == 400, "did not fail on bad json"

    # test the use of default content type
    fn = mlrun.new_function("tests", kind="serving")
    fn.spec.default_content_type = "application/json"
    graph = fn.set_topology("flow", engine="sync")
    graph.to(name="totype", handler=return_type)

    server = fn.to_mock_server()
    resp = server.test(body="[1,2]")
    assert resp == "list", "did not load json"


def test_add_model():
    fn = mlrun.new_function("tests", kind="serving")
    graph = fn.set_topology("flow", engine="sync")
    graph.to("Echo", "e1").to("Echo", "e2")
    try:
        # should fail, we dont have a router
        fn.add_model("m1", class_name="ModelTestingClass", model_path=".")
        assert True, "add_model did not fail without router"
    except Exception:
        pass

    # model should be added to the one (and only) router
    fn = mlrun.new_function("tests", kind="serving")
    graph = fn.set_topology("flow", engine="sync")
    graph.to("Echo", "e1").to("*", "router").to("Echo", "e2")
    fn.add_model("m1", class_name="ModelTestingClass", model_path=".")
    print(graph.to_yaml())

    assert "m1" in graph["router"].routes, "model was not added to router"

    # model is added to the specified router (by name)
    fn = mlrun.new_function("tests", kind="serving")
    graph = fn.set_topology("flow", engine="sync")
    graph.to("Echo", "e1").to("*", "r1").to("Echo", "e2").to("*", "r2")
    fn.add_model("m1", class_name="ModelTestingClass", model_path=".", router_step="r2")
    print(graph.to_yaml())

    assert "m1" in graph["r2"].routes, "model was not added to proper router"


path_control_tests = {"handler": (myfunc2, None), "class": (None, "Mul")}


@pytest.mark.parametrize("test_type", path_control_tests.keys())
@pytest.mark.parametrize("engine", engines)
def test_path_control(engine, test_type):
    function = mlrun.new_function("test", kind="serving")
    flow = function.set_topology("flow", engine=engine)

    handler, class_name = path_control_tests[test_type]

    # function input will be event["x"] and result will be written to event["y"]["z"]
    flow.to(
        class_name, handler=handler, name="x2", input_path="x", result_path="y.z"
    ).respond()

    server = function.to_mock_server()
    resp = server.test(body={"x": 5})
    server.wait_for_completion()
    # expect y.z = x * 2 = 10
    assert resp == {"x": 5, "y": {"z": 10}}, "wrong resp"


def test_path_control_routers():
    function = mlrun.new_function("tests", kind="serving")
    graph = function.set_topology("flow", engine="async")
    graph.to(name="s1", class_name="Echo").to(
        "*", name="r1", input_path="x", result_path="y"
    ).to(name="s3", class_name="Echo").respond()
    function.add_model("m1", class_name="ModelClass", model_path=".")
    logger.info(graph.to_yaml())
    server = function.to_mock_server()

    resp = server.test("/v2/models/m1/infer", body={"x": {"inputs": [5]}})
    server.wait_for_completion()
    print(resp)
    assert resp["y"]["outputs"] == 5, "wrong output"

    function = mlrun.new_function("tests", kind="serving")
    graph = function.set_topology("flow", engine="sync")
    graph.to(name="s1", class_name="Echo").to(
        "*mlrun.serving.routers.VotingEnsemble",
        name="r1",
        input_path="x",
        result_path="y",
        vote_type="regression",
    ).to(name="s3", class_name="Echo").respond()
    function.add_model("m1", class_name="ModelClassList", model_path=".", multiplier=10)
    function.add_model("m2", class_name="ModelClassList", model_path=".", multiplier=20)
    logger.info(graph.to_yaml())
    server = function.to_mock_server()

    resp = server.test("/v2/models/infer", body={"x": {"inputs": [[5]]}})
    server.wait_for_completion()
    # expect avg of (5*10) and (5*20) = 75
    assert resp["y"]["outputs"] == [75], "wrong output"
