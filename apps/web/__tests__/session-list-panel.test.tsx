import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SessionListPanel } from "@/components/session-list-panel";

describe("SessionListPanel", () => {
  it("renders sessions", () => {
    const onRevoke = vi.fn();
    const { container, getByText } = render(
      <SessionListPanel currentSessionId="sess_abc123" onRevoke={onRevoke}
        sessions={[
          { id: "sess_abc123def456gh", ip: "1.2.3.4", userAgent: "Chrome" },
          { id: "sess_xyz789qwe012rs", ip: "5.6.7.8", userAgent: "Firefox" },
        ]} />
    );
    expect(container.textContent).toContain("Active Sessions");
    expect(container.textContent).toContain("1.2.3.4");
    expect(container.textContent).toContain("Chrome");
    expect(container.textContent).toContain("Firefox");
    fireEvent.click(getByText("Revoke"));
    expect(onRevoke).toHaveBeenCalledWith("sess_xyz789qwe012rs");
  });
});
