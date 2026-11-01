import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReadinessDashPanel } from "@/components/readiness-dash-panel";
describe("ReadinessDashPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReadinessDashPanel readyCount={1} notReady={1} readinessPct={50}
        services={[
          { service: "api", score: 6, total: 6, ready: true },
          { service: "worker", score: 3, total: 6, ready: false },
        ]} />
    );
    expect(container.textContent).toContain("Production Readiness");
    expect(container.textContent).toContain("50% ready");
    expect(container.textContent).toContain("1 ready");
    expect(container.textContent).toContain("1 not ready");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("6/6");
    expect(container.textContent).toContain("worker");
    expect(container.textContent).toContain("3/6");
  });
});
