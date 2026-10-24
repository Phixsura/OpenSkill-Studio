import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AuditTrailTimeline } from "@/components/audit-trail-timeline";

describe("AuditTrailTimeline", () => {
  it("renders events", () => {
    const { container } = render(
      <AuditTrailTimeline total={2} events={[
        { seq: 2, actor: "bob", action: "update", resource: "app/123", detail: "changed name", hash: "abc" },
        { seq: 1, actor: "alice", action: "create", resource: "app/123", detail: "", hash: "def" },
      ]} />
    );
    expect(container.textContent).toContain("Audit Trail");
    expect(container.textContent).toContain("2 events");
    expect(container.textContent).toContain("bob");
    expect(container.textContent).toContain("update");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("create");
  });
});
