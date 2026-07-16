import json
from pathlib import Path
from typing import Iterator

import dlt


TRACE_PATH = Path("data/mock_agent_traces.jsonl")


@dlt.resource(name="spans")
def local_agent_spans() -> Iterator[dict]:
    with TRACE_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def main() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="local_agent_traces",
        destination="duckdb",
        dataset_name="agent_traces",
    )

    load_info = pipeline.run(local_agent_spans())
    print(load_info)


if __name__ == "__main__":
    main()