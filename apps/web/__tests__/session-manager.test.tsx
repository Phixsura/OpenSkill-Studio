import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SessionManager } from "@/components/session-manager";

describe("SessionManager", () => {
  const sessions = [
    { device: "Chrome on Mac", ip: "1.2.3.4", created_at: "2026-01-01", active: true, is_current: true },
    { device: "Firefox on Linux", ip: "5.6.7.8", created_at: "2026-01-02", active: true, is_current: false },
  ];
  it("renders sessions", () => {
    const { container } = render(<SessionManager sessions={sessions} onRevoke={vi.fn()} />);
    expect(container.textContent).toContain("Chrome on Mac");
    expect(container.textContent).toContain("Current");
    expect(container.textContent).toContain("2 active");
  });
  it("revoke non-current", () => {
    const fn = vi.fn();
    const { container } = render(<SessionManager sessions={sessions} onRevoke={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith(1);
  });
});
