import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentTracker } from "@/components/incident-tracker";

describe("IncidentTracker", () => {
  const incidents = [
    { id: "INC-ABC1", title: "API outage", severity: "sev1", severityLabel: "Critical", status: "investigating" },
    { id: "INC-DEF2", title: "Slow queries", severity: "sev3", severityLabel: "Minor", status: "resolved" },
  ];
  it("renders incidents", () => {
    const { container } = render(<IncidentTracker incidents={incidents} active={1} hasCritical={true} />);
    expect(container.textContent).toContain("API outage");
    expect(container.textContent).toContain("INC-ABC1");
    expect(container.textContent).toContain("Critical");
    expect(container.textContent).toContain("investigating");
    expect(container.textContent).toContain("1 active");
  });
});
