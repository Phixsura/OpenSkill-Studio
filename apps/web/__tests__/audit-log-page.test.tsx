import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AuditLogPage } from "@/components/audit-log-page";

describe("AuditLogPage", () => {
  const events = [{ action: "login", icon: "🔑", actor: "Alice", target: "", ip: "1.2.3.4", timestamp: "2026-10-01" }];
  it("renders audit log", () => {
    const { container } = render(
      <AuditLogPage events={events} total={1} page={1} totalPages={1}
        availableActions={["login"]} availableActors={["Alice"]}
        onFilter={vi.fn()} onPageChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Audit Log");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("login");
    expect(container.textContent).toContain("1 events");
  });
});
