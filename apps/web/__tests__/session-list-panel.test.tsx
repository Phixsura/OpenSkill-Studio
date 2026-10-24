import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SessionListPanel } from "@/components/session-list-panel";

describe("SessionListPanel", () => {
  it("renders sessions", () => {
    const { container } = render(
      <SessionListPanel activeCount={2} uniqueUsers={1} onRevoke={vi.fn()}
        sessions={[
          { sessionId: "sess_abc", ip: "1.2.3.4", userAgent: "Chrome", active: true },
          { sessionId: "sess_xyz", ip: "5.6.7.8", userAgent: "Firefox", active: false },
        ]} />
    );
    expect(container.textContent).toContain("Active Sessions");
    expect(container.textContent).toContain("2 sessions");
    expect(container.textContent).toContain("sess_abc");
    expect(container.textContent).toContain("Chrome");
    expect(container.textContent).toContain("Revoke");
    expect(container.textContent).toContain("Revoked");
  });
});
