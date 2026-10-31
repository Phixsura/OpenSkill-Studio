import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentTimeline } from "@/components/incident-timeline";

describe("IncidentTimeline", () => {
  it("renders", () => {
    const { container } = render(
      <IncidentTimeline mttrMinutes={20}
        events={[
          { timestamp: 1, phase: "detect", msg: "Alert fired" },
          { timestamp: 2, phase: "triage", msg: "Team paged" },
          { timestamp: 3, phase: "resolve", msg: "Fix deployed" },
        ]} />
    );
    expect(container.textContent).toContain("Incident Timeline");
    expect(container.textContent).toContain("MTTR: 20min");
    expect(container.textContent).toContain("3 events");
    expect(container.textContent).toContain("Alert fired");
    expect(container.textContent).toContain("Fix deployed");
  });
});
