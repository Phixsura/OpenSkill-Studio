import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UpdateNotificationFeed } from "@/components/update-notification-feed";

const notifs = [
  { notifId: "u1", extensionId: "ext-1", oldVersion: "1.0", newVersion: "2.0", changelog: ["Breaking API change"], breaking: true },
  { notifId: "u2", extensionId: "ext-2", oldVersion: "3.0", newVersion: "3.1", changelog: ["Bug fix"], breaking: false },
];

describe("UpdateNotificationFeed", () => {
  it("renders notifications", () => {
    const { container } = render(<UpdateNotificationFeed notifications={notifs} />);
    expect(container.textContent).toContain("BREAKING");
    expect(container.textContent).toContain("1.0 → 2.0");
    expect(container.textContent).toContain("Bug fix");
  });
  it("triggers update", () => {
    const fn = vi.fn();
    const { container } = render(<UpdateNotificationFeed notifications={notifs} onUpdate={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[0]);
    expect(fn).toHaveBeenCalledWith("ext-1", "2.0");
  });
});
