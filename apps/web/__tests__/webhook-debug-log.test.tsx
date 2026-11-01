import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookDebugLog } from "@/components/webhook-debug-log";

describe("WebhookDebugLog", () => {
  it("shows entries", () => {
    const { container } = render(<WebhookDebugLog entries={[{ eventType: "app.installed", statusCode: 200, durationMs: 50, success: true, error: null, timestamp: "10:00" }]} />);
    expect(container.textContent).toContain("app.installed");
  });
  it("empty state", () => {
    const { container } = render(<WebhookDebugLog entries={[]} />);
    expect(container.textContent).toContain("No debug logs");
  });
});
