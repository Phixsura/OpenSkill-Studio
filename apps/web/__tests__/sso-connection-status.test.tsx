import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SSOConnectionStatus } from "@/components/sso-connection-status";

const sessions = [
  { sessionId: "s1", extensionId: "ext-1", extensionName: "Auth Plugin", expiresAt: Date.now() / 1000 + 1800 },
  { sessionId: "s2", extensionId: "ext-2", extensionName: "Dashboard", expiresAt: Date.now() / 1000 + 600 },
];

describe("SSOConnectionStatus", () => {
  it("renders sessions", () => {
    const { container } = render(<SSOConnectionStatus sessions={sessions} />);
    expect(container.textContent).toContain("Auth Plugin");
    expect(container.textContent).toContain("Dashboard");
    expect(container.textContent).toContain("SSO Sessions (2)");
  });
  it("revoke", () => {
    const fn = vi.fn();
    const { container } = render(<SSOConnectionStatus sessions={sessions} onRevoke={fn} />);
    const btns = Array.from(container.querySelectorAll("button")).filter(b => b.textContent === "Revoke");
    fireEvent.click(btns[0]);
    expect(fn).toHaveBeenCalledWith("s1");
  });
});
