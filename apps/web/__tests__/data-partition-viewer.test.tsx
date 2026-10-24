import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataPartitionViewer } from "@/components/data-partition-viewer";

describe("DataPartitionViewer", () => {
  it("renders", () => {
    const { container } = render(
      <DataPartitionViewer numShards={4} maxDeviationPct={5.2} rebalanceNeeded={false}
        distribution={{ "shard-0": 250, "shard-1": 260, "shard-2": 240, "shard-3": 250 }} />
    );
    expect(container.textContent).toContain("Data Partitions");
    expect(container.textContent).toContain("4 shards");
    expect(container.textContent).toContain("5.2% skew");
    expect(container.textContent).toContain("shard-0");
    expect(container.textContent).toContain("250");
  });
});
