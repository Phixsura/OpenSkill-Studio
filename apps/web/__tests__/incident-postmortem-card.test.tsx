import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IncidentPostmortemCard from "../src/components/incident-postmortem-card";

const pm = {
  postmortem_id: "pm1",
  title: "DB Outage Postmortem",
  root_cause: "Connection pool leak under high load",
  impact: "2 hours of downtime, 500 users affected",
  action_items: [
    { description: "Add connection pool monitoring", owner: "alice", completed: true },
    { description: "Fix retry logic", owner: "bob", completed: false },
  ],
  completion_pct: 50,
};

describe("IncidentPostmortemCard", () => {
  it("renders title", () => {
    const { container } = render(<IncidentPostmortemCard postmortem={pm} appName="My App" />);
    expect(container.textContent).toContain("DB Outage Postmortem");
  });

  it("shows completion percentage", () => {
    const { container } = render(<IncidentPostmortemCard postmortem={pm} appName="App" />);
    expect(container.textContent).toContain("50% complete");
  });

  it("shows root cause and impact", () => {
    const { container } = render(<IncidentPostmortemCard postmortem={pm} appName="App" />);
    expect(container.textContent).toContain("Connection pool leak");
    expect(container.textContent).toContain("500 users affected");
  });

  it("renders action items", () => {
    const { container } = render(<IncidentPostmortemCard postmortem={pm} appName="App" />);
    expect(container.textContent).toContain("Add connection pool monitoring");
    expect(container.textContent).toContain("(alice)");
    expect(container.textContent).toContain("1/2");
  });

  it("shows check marks", () => {
    const { container } = render(<IncidentPostmortemCard postmortem={pm} appName="App" />);
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("○");
  });
});
