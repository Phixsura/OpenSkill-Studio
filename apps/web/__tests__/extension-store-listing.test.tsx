import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionStoreListing } from "@/components/extension-store-listing";

const mockExtension = {
  id: "slack-bot", name: "Slack Bot Pro", icon: "💬",
  author: "Alice", version: "2.1.0",
  description: "Advanced Slack integration",
  longDescription: "Slack Bot Pro provides advanced Slack integration including channels, threads, reactions, and file sharing capabilities for the OpenSkill platform.",
  category: "messaging", downloads: 15200, rating: 4.7,
  reviewCount: 89, screenshots: ["overview.png", "config.png"],
  tags: ["slack", "notifications", "messaging"], lastUpdated: "2 days ago",
  installed: false,
};

describe("ExtensionStoreListing", () => {
  it("renders extension details", () => {
    const { container } = render(<ExtensionStoreListing extension={mockExtension} />);
    expect(container.textContent).toContain("Slack Bot Pro");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("15,200");
    expect(container.textContent).toContain("4.7");
  });

  it("renders tags and category", () => {
    const { container } = render(<ExtensionStoreListing extension={mockExtension} />);
    expect(container.textContent).toContain("messaging");
    expect(container.textContent).toContain("slack");
    expect(container.textContent).toContain("notifications");
  });

  it("calls onInstall when not installed", () => {
    const onInstall = vi.fn();
    const { getByText } = render(
      <ExtensionStoreListing extension={mockExtension} onInstall={onInstall} />
    );
    fireEvent.click(getByText("Install"));
    expect(onInstall).toHaveBeenCalled();
  });

  it("shows Uninstall when installed", () => {
    const { getByText } = render(
      <ExtensionStoreListing extension={{ ...mockExtension, installed: true }} />
    );
    expect(getByText("Uninstall")).toBeDefined();
  });
});
