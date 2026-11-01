import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepImpactPanel } from "@/components/dep-impact-panel";
describe("DepImpactPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepImpactPanel totalServices={5}
        impacts={[
          { service: "db", blastRadius: 3, impactPct: 60 },
          { service: "queue", blastRadius: 1, impactPct: 20 },
        ]} />
    );
    expect(container.textContent).toContain("Dependency Impact");
    expect(container.textContent).toContain("5 services analyzed");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("3 svcs (60%)");
    expect(container.textContent).toContain("queue");
  });
});
