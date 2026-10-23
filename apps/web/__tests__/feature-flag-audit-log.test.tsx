import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureFlagAuditLog } from "@/components/feature-flag-audit-log";

describe("FeatureFlagAuditLog", () => {
  const entries = [
    { audit_id: "ffa_1", flag_name: "dark_mode", old_value: false, new_value: true,
      changed_by: "alice", reason: "User request", timestamp: "2026-10-23T12:00:00", change_type: "enabled" },
  ];
  it("renders", () => {
    const { container } = render(<FeatureFlagAuditLog entries={entries} total={1} />);
    expect(container.textContent).toContain("Flag Audit Log");
    expect(container.textContent).toContain("dark_mode");
    expect(container.textContent).toContain("🟢");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("1 changes");
  });
});
