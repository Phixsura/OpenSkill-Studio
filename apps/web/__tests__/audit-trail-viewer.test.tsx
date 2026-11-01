import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AuditTrailViewer } from "@/components/audit-trail-viewer";

const entries = [
  { entryId: "a1", extensionId: "ext-1", actorId: "dev-1", action: "created", details: "v1.0", timestamp: Date.now() / 1000 },
  { entryId: "a2", extensionId: "ext-1", actorId: "dev-1", action: "published", details: "", timestamp: Date.now() / 1000 },
];

describe("AuditTrailViewer", () => {
  it("renders timeline", () => {
    const { container } = render(<AuditTrailViewer entries={entries} />);
    expect(container.textContent).toContain("dev-1");
    expect(container.textContent).toContain("created");
    expect(container.textContent).toContain("published");
  });
  it("empty state", () => {
    const { container } = render(<AuditTrailViewer entries={[]} />);
    expect(container.textContent).toContain("No audit events");
  });
});
