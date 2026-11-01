import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OpsScorePanel } from "@/components/ops-score-panel";
describe("OpsScorePanel", () => {
  it("renders", () => {
    const { container } = render(
      <OpsScorePanel score={92} grade="A" service="api"
        categories={{ reliability: 99.9, performance: 95, observability: 90, documentation: 85, automation: 80, security: 95 }} />
    );
    expect(container.textContent).toContain("92 — A");
    expect(container.textContent).toContain("api Operational Excellence");
    expect(container.textContent).toContain("reliability");
    expect(container.textContent).toContain("99.9");
    expect(container.textContent).toContain("security");
    expect(container.textContent).toContain("95");
  });
});
