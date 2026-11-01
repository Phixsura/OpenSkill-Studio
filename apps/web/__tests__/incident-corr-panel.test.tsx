import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentCorrPanel } from "@/components/incident-corr-panel";
describe("IncidentCorrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <IncidentCorrPanel totalIncidents={4} uncorrelated={1}
        groups={[{ services: ["api", "db", "cache"], count: 3 }]} />
    );
    expect(container.textContent).toContain("Incident Correlation");
    expect(container.textContent).toContain("1 groups");
    expect(container.textContent).toContain("4 incidents");
    expect(container.textContent).toContain("1 uncorrelated");
    expect(container.textContent).toContain("3 incidents");
    expect(container.textContent).toContain("api, db, cache");
  });
});
