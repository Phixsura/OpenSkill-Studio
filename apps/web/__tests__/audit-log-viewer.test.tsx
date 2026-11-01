import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AuditLogViewer } from "@/components/audit-log-viewer";

describe("AuditLogViewer", () => {
  const events = [
    { id: "1", action: "login", actor: "alice", target: "", severity: "info", icon: "ℹ️", ip: "1.2.3.4", timestamp: "2026-01-02" },
    { id: "2", action: "delete_app", actor: "bob", target: "app1", severity: "critical", icon: "🚨", ip: "5.6.7.8", timestamp: "2026-01-01" },
  ];
  const bySeverity = { info: 1, critical: 1 };
  it("renders events", () => {
    const { container } = render(<AuditLogViewer events={events} bySeverity={bySeverity} />);
    expect(container.textContent).toContain("login");
    expect(container.textContent).toContain("delete_app");
    expect(container.textContent).toContain("by alice");
  });
  it("filters", () => {
    const { container } = render(<AuditLogViewer events={events} bySeverity={bySeverity} />);
    const critBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("critical"))!;
    fireEvent.click(critBtn);
    expect(container.textContent).toContain("delete_app");
    expect(container.textContent).not.toContain("login");
  });
});
