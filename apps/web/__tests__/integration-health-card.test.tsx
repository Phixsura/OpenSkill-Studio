import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import IntegrationHealthCard from "../src/components/integration-health-card";

const integrations = [
  {
    integration_id: "stripe",
    name: "Stripe",
    healthy: true,
    availability_pct: 99.9,
    avg_latency_ms: 120,
    last_error: "",
  },
  {
    integration_id: "sendgrid",
    name: "SendGrid",
    healthy: false,
    availability_pct: 85,
    avg_latency_ms: 350,
    last_error: "timeout",
  },
];

describe("IntegrationHealthCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <IntegrationHealthCard integrations={integrations} appName="My App" />,
    );
    expect(container.textContent).toContain("Integrations");
    expect(container.textContent).toContain("My App");
  });

  it("shows down count", () => {
    const { container } = render(
      <IntegrationHealthCard integrations={integrations} appName="App" />,
    );
    expect(container.textContent).toContain("1 down");
  });

  it("shows all-healthy", () => {
    const healthy = [integrations[0]];
    const { container } = render(<IntegrationHealthCard integrations={healthy} appName="App" />);
    expect(container.textContent).toContain("All healthy");
  });

  it("renders names and metrics", () => {
    const { container } = render(
      <IntegrationHealthCard integrations={integrations} appName="App" />,
    );
    expect(container.textContent).toContain("Stripe");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("120ms");
  });

  it("shows error message", () => {
    const { container } = render(
      <IntegrationHealthCard integrations={integrations} appName="App" />,
    );
    expect(container.textContent).toContain("timeout");
  });

  it("shows empty state", () => {
    const { container } = render(<IntegrationHealthCard integrations={[]} appName="App" />);
    expect(container.textContent).toContain("No integrations");
  });
});
