import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SecAuditLogViewer } from "@/components/sec-audit-log-viewer";

describe("SecAuditLogViewer", () => {
  it("renders log", () => {
    const { container } = render(
      <SecAuditLogViewer total={50} bySeverity={{ high: 5, info: 45 }}
        events={[
          { actor: "alice", action: "login", resource: "/auth", result: "success", severity: "info", ip: "1.2.3.4" },
          { actor: "bob", action: "login_failed", resource: "/auth", result: "failure", severity: "high", ip: "5.6.7.8" },
        ]} />
    );
    expect(container.textContent).toContain("Security Audit Log");
    expect(container.textContent).toContain("50 events");
    expect(container.textContent).toContain("5 high");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("login_failed");
    expect(container.textContent).toContain("failure");
  });
});
