import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SessionManagerPanel } from "@/components/session-manager-panel";

describe("SessionManagerPanel", () => {
  const sessions = [
    { session_hash: "cur", ip: "1.2.3.4", device_type: "desktop", user_agent: "Chrome", created_at: "2026-10-23", active: true },
    { session_hash: "old", ip: "5.6.7.8", device_type: "mobile", user_agent: "Safari", created_at: "2026-10-20", active: true },
  ];
  it("renders", () => {
    const { container } = render(
      <SessionManagerPanel sessions={sessions} currentSessionHash="cur" onRevoke={vi.fn()} onRevokeAll={vi.fn()} />
    );
    expect(container.textContent).toContain("Active Sessions");
    expect(container.textContent).toContain("(current)");
    expect(container.textContent).toContain("🖥️");
    expect(container.textContent).toContain("📱");
  });
  it("revoke other", () => {
    const fn = vi.fn();
    const { container } = render(
      <SessionManagerPanel sessions={sessions} currentSessionHash="cur" onRevoke={fn} onRevokeAll={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Revoke")!);
    expect(fn).toHaveBeenCalledWith("old");
  });
});
