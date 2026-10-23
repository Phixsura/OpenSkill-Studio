import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnnouncementBanner } from "@/components/announcement-banner";

describe("AnnouncementBanner", () => {
  it("renders", () => {
    const { container } = render(<AnnouncementBanner title="API v3" body="New features" type="feature" onDismiss={vi.fn()} />);
    expect(container.textContent).toContain("API v3");
    expect(container.textContent).toContain("New features");
  });
  it("dismiss", () => {
    const fn = vi.fn();
    const { container } = render(<AnnouncementBanner title="X" body="Y" type="info" onDismiss={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
