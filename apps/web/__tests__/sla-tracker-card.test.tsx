import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SLATrackerCard from "../src/components/sla-tracker-card";

const metTarget = {
  target_id: "uptime",
  name: "Uptime SLA",
  metric: "uptime_pct",
  threshold: 99.9,
  comparison: "gte" as const,
  current_value: 99.95,
  met: true,
  compliance_pct: 100,
  breaches: 0,
  measurements: 100,
};

const breachedTarget = {
  target_id: "latency",
  name: "Latency SLA",
  metric: "response_time_ms",
  threshold: 200,
  comparison: "lte" as const,
  current_value: 350,
  met: false,
  compliance_pct: 85,
  breaches: 15,
  measurements: 100,
};

describe("SLATrackerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<SLATrackerCard targets={[metTarget]} appName="My App" />);
    expect(container.textContent).toContain("SLA Compliance");
    expect(container.textContent).toContain("My App");
  });

  it("shows all-met badge", () => {
    const { container } = render(<SLATrackerCard targets={[metTarget]} appName="App" />);
    expect(container.textContent).toContain("All met");
  });

  it("shows breached badge", () => {
    const { container } = render(<SLATrackerCard targets={[breachedTarget]} appName="App" />);
    expect(container.textContent).toContain("1 breached");
  });

  it("renders target name and status", () => {
    const { container } = render(
      <SLATrackerCard targets={[metTarget, breachedTarget]} appName="App" />,
    );
    expect(container.textContent).toContain("Uptime SLA");
    expect(container.textContent).toContain("Met");
    expect(container.textContent).toContain("Breached");
  });

  it("shows compliance percentage", () => {
    const { container } = render(<SLATrackerCard targets={[breachedTarget]} appName="App" />);
    expect(container.textContent).toContain("85.0%");
  });

  it("shows threshold comparison", () => {
    const { container } = render(<SLATrackerCard targets={[metTarget]} appName="App" />);
    expect(container.textContent).toContain("≥");
    expect(container.textContent).toContain("99.9");
  });

  it("shows breach count", () => {
    const { container } = render(<SLATrackerCard targets={[breachedTarget]} appName="App" />);
    expect(container.textContent).toContain("15 breaches in 100 checks");
  });

  it("shows empty state", () => {
    const { container } = render(<SLATrackerCard targets={[]} appName="App" />);
    expect(container.textContent).toContain("No SLA targets defined");
  });
});
