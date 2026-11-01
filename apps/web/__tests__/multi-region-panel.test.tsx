import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MultiRegionPanel } from "@/components/multi-region-panel";

describe("MultiRegionPanel", () => {
  it("renders regions", () => {
    const onFailover = vi.fn();
    const { container, getByText } = render(
      <MultiRegionPanel primary="us-east" status="healthy" onFailover={onFailover}
        regions={[
          { id: "us-east", label: "US East", healthy: true, trafficPct: 50 },
          { id: "eu-west", label: "EU West", healthy: true, trafficPct: 50 },
        ]} />
    );
    expect(container.textContent).toContain("Multi-Region");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("US East");
    expect(container.textContent).toContain("Primary");
    expect(container.textContent).toContain("50%");
    fireEvent.click(getByText("Promote"));
    expect(onFailover).toHaveBeenCalledWith("eu-west");
  });
});
