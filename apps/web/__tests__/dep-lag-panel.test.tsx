import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepLagPanel } from "@/components/dep-lag-panel";
describe("DepLagPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepLagPanel laggingCount={1} thresholdMs={100}
        pairs={[{ source: "api", destination: "db", avgMs: 350, maxMs: 400, calls: 50 }]} />
    );
    expect(container.textContent).toContain("Dependency Lag");
    expect(container.textContent).toContain("1 lagging");
    expect(container.textContent).toContain("api → db");
    expect(container.textContent).toContain("avg 350ms");
    expect(container.textContent).toContain("max 400ms");
  });
});
