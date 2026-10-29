import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIAuditLogCard from "../src/components/api-developer-api-audit-log-card";

const entries = [
  { entry_id: "e1", actor: "alice", action: "create", resource_type: "api_key", resource_id: "k1", ip_address: "1.2.3.4" },
  { entry_id: "e2", actor: "bob", action: "delete", resource_type: "webhook", resource_id: "w1", ip_address: "5.6.7.8" },
];

describe("APIDeveloperAPIAuditLogCard", () => {
  it("shows audit entries", () => {
    const { container } = render(<APIDeveloperAPIAuditLogCard entries={entries} totalCount={250} appName="App" />);
    expect(container.textContent).toContain("Audit Log");
    expect(container.textContent).toContain("250 entries");
    expect(container.textContent).toContain("create");
    expect(container.textContent).toContain("api_key/k1");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("delete");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIAuditLogCard entries={[]} totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No audit entries");
  });
});
