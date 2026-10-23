import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SmartNotificationCenter } from "@/components/smart-notification-center";

describe("SmartNotificationCenter", () => {
  it("renders items", () => {
    const items = [
      { type: "single", title: "New Install", message: "App installed by Acme" },
      { type: "batch", category: "reviews", summary: "3 new reviews", count: 3 },
    ];
    const { container } = render(<SmartNotificationCenter items={items} onDismiss={vi.fn()} />);
    expect(container.textContent).toContain("New Install");
    expect(container.textContent).toContain("3 new reviews");
  });
  it("empty state", () => {
    const { container } = render(<SmartNotificationCenter items={[]} onDismiss={vi.fn()} />);
    expect(container.textContent).toContain("All caught up");
  });
  it("dismiss", () => {
    const fn = vi.fn();
    const items = [{ type: "single", title: "X" }];
    const { container } = render(<SmartNotificationCenter items={items} onDismiss={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith(0);
  });
});
