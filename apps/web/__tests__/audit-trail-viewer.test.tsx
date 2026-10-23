import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AuditTrailViewer } from "@/components/audit-trail-viewer";

describe("AuditTrailViewer", () => {
  const entries = [
    { entry_id: "a1", actor: "admin", action: "delete_app", resource: "app_123",
      timestamp: "2026-10-23T12:00:00", hash: "abc123def456789012345678" },
  ];
  it("renders", () => {
    const { container } = render(
      <AuditTrailViewer entries={entries} chainValid={true} onVerify={vi.fn()} />
    );
    expect(container.textContent).toContain("Audit Trail");
    expect(container.textContent).toContain("🔗 Chain Valid");
    expect(container.textContent).toContain("admin");
    expect(container.textContent).toContain("delete_app");
  });
  it("verify", () => {
    const fn = vi.fn();
    const { container } = render(
      <AuditTrailViewer entries={entries} chainValid={true} onVerify={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Verify")!);
    expect(fn).toHaveBeenCalled();
  });
});
