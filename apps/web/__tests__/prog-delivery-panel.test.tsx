import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ProgDeliveryPanel } from "@/components/prog-delivery-panel";

describe("ProgDeliveryPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ProgDeliveryPanel deployment="api-v3" currentStage={1} status="in_progress"
        stages={[
          { stage: 1, name: "canary", trafficPct: 5, status: "completed" },
          { stage: 2, name: "partial", trafficPct: 50, status: "pending" },
          { stage: 3, name: "full", trafficPct: 100, status: "pending" },
        ]} />
    );
    expect(container.textContent).toContain("Progressive: api-v3");
    expect(container.textContent).toContain("Stage 2");
    expect(container.textContent).toContain("canary");
    expect(container.textContent).toContain("5%");
    expect(container.textContent).toContain("partial");
    expect(container.textContent).toContain("full");
  });
});
