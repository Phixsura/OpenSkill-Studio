import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AuditLogCard from "../src/components/audit-log-card";

const infoEvent = {
  event_id: "evt-1",
  actor: "user-1",
  action: "key.created",
  resource_type: "api_key",
  resource_id: "k1",
  severity: "info" as const,
  details: "Created production API key",
  ip_address: "10.0.0.1",
  timestamp: new Date(Date.now() - 300_000).toISOString(),
};

const criticalEvent = {
  event_id: "evt-2",
  actor: "system",
  action: "key.revoked",
  resource_type: "api_key",
  resource_id: "k2",
  severity: "critical" as const,
  details: "Key compromised — auto-revoked",
  ip_address: "",
  timestamp: new Date(Date.now() - 60_000).toISOString(),
};

const warningEvent = {
  event_id: "evt-3",
  actor: "user-2",
  action: "config.updated",
  resource_type: "config",
  resource_id: "c1",
  severity: "warning" as const,
  details: "",
  ip_address: "192.168.1.1",
  timestamp: new Date(Date.now() - 3_600_000).toISOString(),
};

describe("AuditLogCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <AuditLogCard events={[infoEvent]} appName="My App" totalCount={42} />,
    );
    expect(container.textContent).toContain("Audit Log");
    expect(container.textContent).toContain("My App");
  });

  it("shows total count", () => {
    const { container } = render(
      <AuditLogCard events={[infoEvent]} appName="App" totalCount={1234} />,
    );
    expect(container.textContent).toContain("1,234 total");
  });

  it("shows critical badge", () => {
    const { container } = render(
      <AuditLogCard events={[criticalEvent]} appName="App" totalCount={10} />,
    );
    expect(container.textContent).toContain("1 critical");
  });

  it("renders action and resource", () => {
    const { container } = render(
      <AuditLogCard events={[infoEvent]} appName="App" totalCount={1} />,
    );
    expect(container.textContent).toContain("key.created");
    expect(container.textContent).toContain("api_key/k1");
  });

  it("shows actor and IP", () => {
    const { container } = render(
      <AuditLogCard events={[infoEvent]} appName="App" totalCount={1} />,
    );
    expect(container.textContent).toContain("user-1");
    expect(container.textContent).toContain("10.0.0.1");
  });

  it("shows details", () => {
    const { container } = render(
      <AuditLogCard events={[infoEvent]} appName="App" totalCount={1} />,
    );
    expect(container.textContent).toContain("Created production API key");
  });

  it("hides IP when empty", () => {
    const { container } = render(
      <AuditLogCard events={[criticalEvent]} appName="App" totalCount={1} />,
    );
    expect(container.textContent).not.toContain("10.0.0.1");
  });

  it("renders multiple events", () => {
    const { container } = render(
      <AuditLogCard
        events={[infoEvent, criticalEvent, warningEvent]}
        appName="App"
        totalCount={3}
      />,
    );
    expect(container.textContent).toContain("key.created");
    expect(container.textContent).toContain("key.revoked");
    expect(container.textContent).toContain("config.updated");
  });

  it("shows empty state", () => {
    const { container } = render(<AuditLogCard events={[]} appName="App" totalCount={0} />);
    expect(container.textContent).toContain("No audit events");
  });
});
