import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InfraOverviewPanel } from "@/components/infra-overview-panel";

describe("InfraOverviewPanel", () => {
  it("renders", () => {
    const { container } = render(
      <InfraOverviewPanel displayCost="$10,500/mo" health="healthy"
        nodes={20} cpuCores={160} memoryGb={640} storageTb={50} bandwidthGbps={10} />
    );
    expect(container.textContent).toContain("Infrastructure");
    expect(container.textContent).toContain("$10,500/mo");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("20");
    expect(container.textContent).toContain("160 cores");
    expect(container.textContent).toContain("640 GB");
    expect(container.textContent).toContain("50 TB");
  });
});
