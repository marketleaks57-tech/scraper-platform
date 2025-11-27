import os

import pytest

from src.governance.openfeature import is_enabled, override_flags
from src.governance.openfeature_flags import FEATURE_FLAGS, FeatureFlag
from src.governance.rollout_strategies import AttributeEqualsStrategy, EnvironmentMatchStrategy, PercentageRollout


@pytest.fixture(autouse=True)
def clear_env_flags(monkeypatch):
    monkeypatch.delenv("FEATURE_FLAGS", raising=False)


def test_percentage_rollout_is_stable_per_actor():
    flag = FeatureFlag(
        key="example.rollout",
        strategies=[PercentageRollout(percentage=50.0, bucket_by="actor_id")],
    )
    assert flag.evaluate({"actor_id": "user-a"}) == flag.evaluate({"actor_id": "user-a"})
    assert flag.evaluate({"actor_id": "user-b"}) == flag.evaluate({"actor_id": "user-b"})


def test_percentage_rollout_respects_bucket_boundaries():
    fifty_flag = FeatureFlag(
        key="example.rollout",
        strategies=[PercentageRollout(percentage=50.0)],
    )
    # Select actors with deterministic buckets to test the boundary around 50.
    enabled_context = {"actor_id": "actor-0"}  # bucket: 26
    disabled_context = {"actor_id": "actor-5"}  # bucket: 64

    assert fifty_flag.evaluate(enabled_context) is True
    assert fifty_flag.evaluate(disabled_context) is False


def test_environment_strategy_enables_only_for_target_env():
    strategy = EnvironmentMatchStrategy(allowed=("staging", "qa"))
    flag = FeatureFlag(key="example.env", strategies=[strategy])

    assert flag.evaluate({"env": "staging"}) is True
    assert flag.evaluate({"env": "prod"}) is False
    assert flag.evaluate({}) is False


def test_attribute_equals_strategy_matches_expected_value():
    flag = FeatureFlag(
        key="example.attr",
        strategies=[AttributeEqualsStrategy(key="tenant", expected_value="beta")],
    )

    assert flag.evaluate({"tenant": "beta"}) is True
    assert flag.evaluate({"tenant": "stable"}) is False
    assert flag.evaluate({}) is False


@pytest.mark.parametrize("override_value", [True, False])
def test_override_flags_takes_precedence(override_value: bool):
    with override_flags({"pcid.vector_store.remote_backend": override_value}):
        assert (
            is_enabled(
                "pcid.vector_store.remote_backend",
                context={"actor_id": "rollout-test"},
            )
            is override_value
        )


def test_default_catalog_flags_are_exposed():
    for key in (
        "pcid.vector_store.similarity_fallback",
        "pcid.vector_store.remote_backend",
        "agents.selector_patch.rollout",
        "governance.force_local_replay",
    ):
        assert key in FEATURE_FLAGS


def test_env_overrides_apply():
    original = os.environ.get("FEATURE_FLAGS")
    os.environ["FEATURE_FLAGS"] = '{"pcid.vector_store.similarity_fallback": false}'
    assert is_enabled("pcid.vector_store.similarity_fallback") is False
    if original is not None:
        os.environ["FEATURE_FLAGS"] = original
    else:
        os.environ.pop("FEATURE_FLAGS", None)
