import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StartupOrderPanel } from "@/components/startup-order-panel";
describe("StartupOrderPanel", () => {
  it("renders", () => {
    const { container } = render(
      <StartupOrderPanel hasCycle={false} total={5}
        phases={[["cache", "db", "queue"], ["api", "worker"]]} />
    );
    expect(container.textContent).toContain("Startup Order");
    expect(container.textContent).toContain("2 phases");
    expect(container.textContent).toContain("5 services");
    expect(container.textContent).toContain("Phase 1");
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("Phase 2");
    expect(container.textContent).toContain("api");
  });
});
