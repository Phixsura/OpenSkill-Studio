import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigAuditPanel } from "@/components/config-audit-panel";
describe("ConfigAuditPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ConfigAuditPanel totalChanges={50}
        entries={[
          { key: "db_host", changedBy: "alice", env: "prod", oldHash: "abc123", newHash: "def456" },
        ]} />
    );
    expect(container.textContent).toContain("Config Audit");
    expect(container.textContent).toContain("50 changes");
    expect(container.textContent).toContain("db_host");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("abc123 → def456");
  });
});
