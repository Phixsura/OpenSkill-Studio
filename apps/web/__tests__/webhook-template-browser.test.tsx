import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookTemplateBrowser } from "@/components/webhook-template-browser";

const templates = [
  { templateId: "install", name: "Extension Installed", eventType: "extension.installed", payloadSchema: { extension_id: "string" }, description: "" },
  { templateId: "review", name: "New Review", eventType: "extension.review.created", payloadSchema: { rating: "number" }, description: "" },
];

describe("WebhookTemplateBrowser", () => {
  it("renders templates and search", () => {
    const { container } = render(<WebhookTemplateBrowser templates={templates} />);
    expect(container.textContent).toContain("Extension Installed");
    expect(container.querySelector("input")).toBeTruthy();
  });
  it("shows schema on click", () => {
    const { container } = render(<WebhookTemplateBrowser templates={templates} />);
    const buttons = container.querySelectorAll("button");
    fireEvent.click(buttons[0]);
    expect(container.textContent).toContain("Payload Schema");
  });
});
