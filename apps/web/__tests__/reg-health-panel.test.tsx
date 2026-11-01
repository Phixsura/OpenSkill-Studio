import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RegHealthPanel } from "@/components/reg-health-panel";
describe("RegHealthPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RegHealthPanel total={4} healthy={2} stale={1} healthPct={50}
        orphans={["old-svc"]} unregistered={["new-svc"]} />
    );
    expect(container.textContent).toContain("Registry Health");
    expect(container.textContent).toContain("50% healthy");
    expect(container.textContent).toContain("Orphans: old-svc");
    expect(container.textContent).toContain("Unregistered: new-svc");
  });
});
