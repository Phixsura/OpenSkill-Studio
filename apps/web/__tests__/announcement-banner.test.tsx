import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnnouncementBanner } from "@/components/announcement-banner";

const anns = [
  { id: "a1", title: "New Feature!", body: "Dark mode", type: "feature" as const, dismissible: true },
  { id: "a2", title: "Maintenance", body: "Scheduled", type: "maintenance" as const, dismissible: false },
];

describe("AnnouncementBanner", () => {
  it("renders announcements", () => {
    const { container } = render(<AnnouncementBanner announcements={anns} />);
    expect(container.textContent).toContain("New Feature!");
    expect(container.textContent).toContain("Maintenance");
  });
  it("calls onDismiss for dismissible", () => {
    const fn = vi.fn();
    const { container } = render(<AnnouncementBanner announcements={anns} onDismiss={fn} />);
    const dismissBtn = container.querySelector("button");
    if (dismissBtn) fireEvent.click(dismissBtn);
    expect(fn).toHaveBeenCalledWith("a1");
  });
});
