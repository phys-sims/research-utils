"""Deterministic experiment script generation helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExperimentScriptSpec:
    """Specification for a generated downstream experiment script."""

    name: str
    adapter_import: str
    parameter_paths: tuple[str, ...]
    base_config: dict[str, Any]
    entrypoint: str = "run"
    seed_policy: str = "explicit-seed-required"


@dataclass(frozen=True)
class ScriptProvenance:
    """Metadata used to annotate generated artifacts."""

    package_version: str
    git_commit: str
    generator: str = "sim_utils.agents.experiment_gen"

    def to_json(self) -> str:
        return json.dumps(
            {
                "generator": self.generator,
                "git_commit": self.git_commit,
                "package_version": self.package_version,
            },
            sort_keys=True,
        )


def generate_experiment_script(
    spec: ExperimentScriptSpec,
    *,
    output_dir: str | Path = "experiments",
    generated_at: datetime,
    provenance: ScriptProvenance,
) -> Path:
    """Generate a deterministic downstream script under ``experiments/``."""
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    filename = _safe_filename(spec.name)
    destination = output_root / f"{filename}.py"

    config_hash = _config_hash(spec)
    timestamp = _timestamp_iso(generated_at)
    script_text = _render_script(
        spec=spec,
        timestamp=timestamp,
        config_hash=config_hash,
        provenance=provenance,
    )
    destination.write_text(script_text, encoding="utf-8")
    return destination


def _render_script(
    *,
    spec: ExperimentScriptSpec,
    timestamp: str,
    config_hash: str,
    provenance: ScriptProvenance,
) -> str:
    parameter_paths = "\n".join(
        f'    "{path}",' for path in sorted(spec.parameter_paths)
    )
    base_config = json.dumps(spec.base_config, indent=2, sort_keys=True)

    return (
        "#!/usr/bin/env python3\n"
        f"# timestamp: {timestamp}\n"
        f"# seed_policy: {spec.seed_policy}\n"
        f"# config_hash: {config_hash}\n"
        f"# provenance: {provenance.to_json()}\n\n"
        "from __future__ import annotations\n\n"
        "import json\n"
        "from pathlib import Path\n\n"
        f"from {spec.adapter_import} import {spec.entrypoint}\n\n"
        "PARAMETER_PATHS = (\n"
        f"{parameter_paths}\n"
        ")\n\n"
        "BASE_CONFIG = "
        f"{base_config}\n\n"
        "def main(*, seed: int) -> None:\n"
        "    result = "
        f"{spec.entrypoint}(config=BASE_CONFIG, seed=seed)\n"
        "    destination = Path(\"results\") / \"result.json\"\n"
        "    destination.parent.mkdir(parents=True, exist_ok=True)\n"
        "    destination.write_text(json.dumps(result, sort_keys=True), encoding=\"utf-8\")\n\n"
        "if __name__ == \"__main__\":\n"
        "    main(seed=0)\n"
    )


def _safe_filename(name: str) -> str:
    return "".join(char if char.isalnum() or char in {"_", "-"} else "_" for char in name)


def _config_hash(spec: ExperimentScriptSpec) -> str:
    payload = {
        "adapter_import": spec.adapter_import,
        "base_config": spec.base_config,
        "entrypoint": spec.entrypoint,
        "name": spec.name,
        "parameter_paths": sorted(spec.parameter_paths),
        "seed_policy": spec.seed_policy,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _timestamp_iso(generated_at: datetime) -> str:
    if generated_at.tzinfo is None:
        aware = generated_at.replace(tzinfo=timezone.utc)
    else:
        aware = generated_at.astimezone(timezone.utc)
    return aware.isoformat().replace("+00:00", "Z")


__all__ = [
    "ExperimentScriptSpec",
    "ScriptProvenance",
    "generate_experiment_script",
]
