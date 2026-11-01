import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RollbackControlPanel } from "@/components/rollback-control-panel";

describe("RollbackControlPanel", () => {
  it("renders panel", () => {
    const { container } = render(
      <RollbackControlPanel currentVersion="2.0" onRollback={vi.fn()}
        snapshots={[{ version: "2.0", status: "available" }, { version: "1.0", status: "available" }]}
        lastRollback={{ fromVersion: "2.0", toVersion: "1.0", changes: [{ key: "db", from: "pg15", to: "pg14" }] }} />
    );
    expect(container.textContent).toContain("Rollback Control");
    expect(container.textContent).toContain("Current: v2.0");
    expect(container.textContent).toContain("v1.0");
    expect(container.textContent).toContain("Rollback");
    expect(container.textContent).toContain("1 changes");
  });
});
