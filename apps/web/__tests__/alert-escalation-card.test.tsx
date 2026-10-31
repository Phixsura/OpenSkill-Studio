import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AlertEscalationCard from "../src/components/alert-escalation-card";

const tiers = [
  { tier: 0, name: "On-call", timeout_seconds: 300 },
  { tier: 1, name: "Manager", timeout_seconds: 600 },
];

const alerts = [
  {
    alert_id: "a1",
    current_tier: 1,
    tier_name: "Manager",
    acknowledged: false,
    acknowledged_by: "",
  },
  {
    alert_id: "a2",
    current_tier: 0,
    tier_name: "On-call",
    acknowledged: true,
    acknowledged_by: "alice",
  },
];

describe("AlertEscalationCard", () => {
  it("renders header", () => {
    const { container } = render(
      <AlertEscalationCard alerts={alerts} tiers={tiers} appName="My App" />,
    );
    expect(container.textContent).toContain("Alert Escalation");
  });

  it("shows unacked count", () => {
    const { container } = render(
      <AlertEscalationCard alerts={alerts} tiers={tiers} appName="App" />,
    );
    expect(container.textContent).toContain("1 unacked");
  });

  it("shows all-clear when none unacked", () => {
    const acked = alerts.map((a) => ({ ...a, acknowledged: true, acknowledged_by: "alice" }));
    const { container } = render(
      <AlertEscalationCard alerts={acked} tiers={tiers} appName="App" />,
    );
    expect(container.textContent).toContain("All clear");
  });

  it("renders tier definitions", () => {
    const { container } = render(
      <AlertEscalationCard alerts={alerts} tiers={tiers} appName="App" />,
    );
    expect(container.textContent).toContain("T0: On-call");
    expect(container.textContent).toContain("T1: Manager");
  });

  it("shows alert details", () => {
    const { container } = render(
      <AlertEscalationCard alerts={alerts} tiers={tiers} appName="App" />,
    );
    expect(container.textContent).toContain("a1");
    expect(container.textContent).toContain("escalating");
    expect(container.textContent).toContain("ack by alice");
  });

  it("shows empty state", () => {
    const { container } = render(<AlertEscalationCard alerts={[]} tiers={tiers} appName="App" />);
    expect(container.textContent).toContain("No active alerts");
  });
});
