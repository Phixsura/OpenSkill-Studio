import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepStalenessPanel } from "@/components/dep-staleness-panel";
describe("DepStalenessPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DepStalenessPanel current={1} stalenessPct={66.7} maxAgeDays={180}
        stale={[
          { name: "lodash", currentVersion: "4.17.20", latestVersion: "4.17.21", ageDays: 365 },
          { name: "react", currentVersion: "18.2", latestVersion: "18.3", ageDays: 200 },
        ]} />
    );
    expect(container.textContent).toContain("Dependency Staleness");
    expect(container.textContent).toContain("2 stale");
    expect(container.textContent).toContain("180d policy");
    expect(container.textContent).toContain("lodash");
    expect(container.textContent).toContain("365d old");
    expect(container.textContent).toContain("4.17.20 → 4.17.21");
  });
});
