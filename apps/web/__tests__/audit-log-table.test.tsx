import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AuditLogTable } from "@/components/audit-log-table";

describe("AuditLogTable", () => {
  const entries = [
    { log_id: "a1", actor_id: "u1", action: "login", resource_type: "session", resource_id: "s1", timestamp: "2026-10-23T12:00:00" },
  ];
  it("renders", () => {
    const { container } = render(<AuditLogTable entries={entries} total={1} onFilter={vi.fn()} />);
    expect(container.textContent).toContain("Audit Log");
    expect(container.textContent).toContain("1 entries");
    expect(container.textContent).toContain("login");
    expect(container.textContent).toContain("session/s1");
  });
  it("filter on actor click", () => {
    const fn = vi.fn();
    const { container } = render(<AuditLogTable entries={entries} total={1} onFilter={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith("actor", "u1");
  });
});
