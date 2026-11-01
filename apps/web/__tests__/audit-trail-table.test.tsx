import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AuditTrailTable } from "@/components/audit-trail-table";

describe("AuditTrailTable", () => {
  it("renders trail", () => {
    const { container } = render(
      <AuditTrailTable totalEvents={50} events={[
        { id: "a1", actor: "alice", action: "create", resource: "app/myapp", details: "Created", ip: "" },
        { id: "a2", actor: "bob", action: "delete", resource: "user/u1", details: "Removed", ip: "1.2.3.4" },
      ]} />
    );
    expect(container.textContent).toContain("Audit Trail");
    expect(container.textContent).toContain("50 events");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("create");
    expect(container.textContent).toContain("app/myapp");
    expect(container.textContent).toContain("bob");
    expect(container.textContent).toContain("delete");
  });
});
