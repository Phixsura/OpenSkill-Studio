import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IncidentTimerPanel } from "@/components/incident-timer-panel";
describe("IncidentTimerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <IncidentTimerPanel avgAckMinutes={5} avgResolveMinutes={30}
        ackSlaPct={80} totalIncidents={10} slaMet={8} />
    );
    expect(container.textContent).toContain("Incident Response");
    expect(container.textContent).toContain("80% SLA met");
    expect(container.textContent).toContain("5min");
    expect(container.textContent).toContain("30min");
    expect(container.textContent).toContain("8/10");
  });
});
