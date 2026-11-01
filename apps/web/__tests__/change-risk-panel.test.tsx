import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangeRiskPanel } from "@/components/change-risk-panel";
describe("ChangeRiskPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ChangeRiskPanel score={85} level="critical" changeDescription="Remove /api/v1/legacy"
        tags={["breaking", "auth", "high_impact"]} />
    );
    expect(container.textContent).toContain("85/100 — CRITICAL");
    expect(container.textContent).toContain("Remove /api/v1/legacy");
    expect(container.textContent).toContain("breaking");
    expect(container.textContent).toContain("auth");
    expect(container.textContent).toContain("high_impact");
  });
});
