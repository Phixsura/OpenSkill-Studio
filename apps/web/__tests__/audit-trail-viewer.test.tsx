import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AuditTrailViewer } from "@/components/audit-trail-viewer";

describe("AuditTrailViewer", () => {
  it("renders", () => {
    const { container } = render(
      <AuditTrailViewer chainValid={true} total={3}
        entries={[
          { seq: 1, actor: "admin", action: "create", resource: "user:1" },
          { seq: 2, actor: "admin", action: "update", resource: "user:1" },
          { seq: 3, actor: "system", action: "delete", resource: "user:2" },
        ]} />
    );
    expect(container.textContent).toContain("Audit Trail");
    expect(container.textContent).toContain("chain valid");
    expect(container.textContent).toContain("3 entries");
    expect(container.textContent).toContain("create");
    expect(container.textContent).toContain("user:1");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("delete");
  });
});
