import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookConfigForm } from "@/components/webhook-config-form";

const EVENTS = ["submission.completed", "app.installed", "cohort.member_added"];

describe("WebhookConfigForm", () => {
  it("renders URL input", () => {
    const { container } = render(<WebhookConfigForm availableEvents={EVENTS} onSave={vi.fn()} />);
    expect(container.querySelector("input[type='url']")).toBeTruthy();
  });

  it("shows event buttons", () => {
    const { container } = render(<WebhookConfigForm availableEvents={EVENTS} onSave={vi.fn()} />);
    expect(container.textContent).toContain("submission.completed");
  });

  it("has save button", () => {
    const { container } = render(<WebhookConfigForm availableEvents={EVENTS} onSave={vi.fn()} />);
    expect(container.textContent).toContain("Save Webhook");
  });

  it("pre-fills URL", () => {
    const { container } = render(<WebhookConfigForm initialUrl="https://x.com" availableEvents={EVENTS} onSave={vi.fn()} />);
    expect((container.querySelector("input") as HTMLInputElement)?.value).toBe("https://x.com");
  });
});
