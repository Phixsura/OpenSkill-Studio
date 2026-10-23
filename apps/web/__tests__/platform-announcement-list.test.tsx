import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlatformAnnouncementList } from "@/components/platform-announcement-list";

describe("PlatformAnnouncementList", () => {
  const anns = [
    { announcement_id: "p1", title: "New Feature", content: "Dark mode!", priority: "high", published_at: "2026-10-23" },
  ];
  it("renders", () => {
    const { container } = render(<PlatformAnnouncementList announcements={anns} onDismiss={vi.fn()} />);
    expect(container.textContent).toContain("New Feature");
    expect(container.textContent).toContain("Dark mode!");
    expect(container.textContent).toContain("⚠️");
  });
  it("dismiss", () => {
    const fn = vi.fn();
    const { container } = render(<PlatformAnnouncementList announcements={anns} onDismiss={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "✕")!);
    expect(fn).toHaveBeenCalledWith("p1");
  });
  it("empty", () => {
    const { container } = render(<PlatformAnnouncementList announcements={[]} onDismiss={vi.fn()} />);
    expect(container.innerHTML).toBe("");
  });
});
