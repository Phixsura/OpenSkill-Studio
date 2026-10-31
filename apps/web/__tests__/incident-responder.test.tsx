import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentResponder } from "@/components/incident-responder";

describe("IncidentResponder", () => {
  it("renders incidents", () => {
    const { container } = render(
      <IncidentResponder open={1} resolved={2} bySeverity={{ critical: 2, major: 1 }}
        incidents={[
          { title: "DB Outage", severity: "critical", status: "investigating",
            affected: ["database", "api"], responders: ["alice", "bob"] },
          { title: "Slow API", severity: "major", status: "resolved",
            affected: ["api"], responders: ["carol"] },
        ]} />
    );
    expect(container.textContent).toContain("Incident Response");
    expect(container.textContent).toContain("1 open");
    expect(container.textContent).toContain("2 resolved");
    expect(container.textContent).toContain("DB Outage");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("database, api");
    expect(container.textContent).toContain("2 responders");
  });
});
