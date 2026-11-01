import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AutoTriagePanel } from "@/components/auto-triage-panel";

describe("AutoTriagePanel", () => {
  it("renders", () => {
    const { container } = render(
      <AutoTriagePanel total={3} byTeam={{ "data-eng": 1 }} bySeverity={{ critical: 1 }}
        triages={[
          { incidentType: "database", assignedTeam: "data-eng", severity: "critical", escalate: true },
          { incidentType: "ui", assignedTeam: "frontend", severity: "low", escalate: false },
        ]} />
    );
    expect(container.textContent).toContain("Auto-Triage");
    expect(container.textContent).toContain("3 triaged");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("data-eng");
    expect(container.textContent).toContain("critical");
  });
});
