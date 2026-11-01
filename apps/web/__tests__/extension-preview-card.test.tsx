import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionPreviewCard } from "@/components/extension-preview-card";

const ext = { name: "Slack Bot", icon: "🤖", description: "Slack integration", rating: 4.5, installs: 10000, category: "comm", developer: "alice" };

describe("ExtensionPreviewCard", () => {
  it("renders extension", () => {
    const { container } = render(<ExtensionPreviewCard ext={ext} />);
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("4.5");
    expect(container.textContent).toContain("10,000");
  });
  it("calls onInstall", () => {
    const fn = vi.fn();
    const { getByText } = render(<ExtensionPreviewCard ext={ext} onInstall={fn} />);
    fireEvent.click(getByText("Install"));
    expect(fn).toHaveBeenCalled();
  });
});
