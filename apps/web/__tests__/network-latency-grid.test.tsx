import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NetworkLatencyGrid } from "@/components/network-latency-grid";

describe("NetworkLatencyGrid", () => {
  const regions = [{ id: "us-east", label: "US East" }, { id: "eu-west", label: "Europe" }];
  const edges = [{ from: "us-east", to: "eu-west", latency_ms: 85, quality: "good" }];
  it("renders", () => {
    const { container } = render(
      <NetworkLatencyGrid regions={regions} edges={edges} userRegion="us-east" />
    );
    expect(container.textContent).toContain("Network Latency");
    expect(container.textContent).toContain("US East");
    expect(container.textContent).toContain("Europe");
    expect(container.textContent).toContain("85ms");
  });
});
