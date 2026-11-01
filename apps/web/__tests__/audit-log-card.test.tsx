import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AuditLogCard from "../src/components/audit-log-card";

const entries = [
  {
    entry_id: "e1",
    actor: "alice",
    action: "create",
    resource_type: "app",
    resource_id: "app-1",
    detail: "",
  },
  {
    entry_id: "e2",
    actor: "bob",
    action: "delete",
    resource_type: "webhook",
    resource_id: "wh-1",
    detail: "",
  },
  {
    entry_id: "e3",
    actor: "alice",
    action: "login",
    resource_type: "session",
    resource_id: "s-1",
    detail: "",
  },
];

describe("AuditLogCard", () => {
  it("renders header and total", () => {
    const { container } = render(<AuditLogCard entries={entries} totalCount={100} appName="App" />);
    expect(container.textContent).toContain("Audit Log");
    expect(container.textContent).toContain("100 entries");
  });

  it("shows action badges", () => {
    const { container } = render(<AuditLogCard entries={entries} totalCount={3} appName="App" />);
    expect(container.textContent).toContain("create");
    expect(container.textContent).toContain("delete");
    expect(container.textContent).toContain("login");
  });

  it("shows resources and actors", () => {
    const { container } = render(<AuditLogCard entries={entries} totalCount={3} appName="App" />);
    expect(container.textContent).toContain("app/app-1");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("bob");
  });

  it("shows empty state", () => {
    const { container } = render(<AuditLogCard entries={[]} totalCount={0} appName="App" />);
    expect(container.textContent).toContain("No audit entries");
  });
});
