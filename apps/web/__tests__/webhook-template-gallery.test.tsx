import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookTemplateGallery } from "@/components/webhook-template-gallery";

const templates = [
  { templateId: "github-push", provider: "github", name: "GitHub Push",
    description: "Push events", icon: "🐙", events: ["push", "pull_request"] },
  { templateId: "slack-notify", provider: "slack", name: "Slack Notification",
    description: "Send to Slack", icon: "💬", events: ["message"] },
];

describe("WebhookTemplateGallery", () => {
  it("renders templates", () => {
    const { container } = render(<WebhookTemplateGallery templates={templates} />);
    expect(container.textContent).toContain("GitHub Push");
    expect(container.textContent).toContain("Slack Notification");
    expect(container.textContent).toContain("push");
  });
  it("calls onUse", () => {
    const fn = vi.fn();
    const { getAllByText } = render(<WebhookTemplateGallery templates={templates} onUse={fn} />);
    fireEvent.click(getAllByText("Use")[0]);
    expect(fn).toHaveBeenCalledWith("github-push");
  });
});
