import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookTestResult } from "@/components/webhook-test-result";

describe("WebhookTestResult", () => {
  it("shows success", () => {
    const { container } = render(<WebhookTestResult success={true} statusCode={200} durationMs={50} verdict="✅ Working" responsePreview='{"ok":true}' />);
    expect(container.textContent).toContain("Working");
    expect(container.textContent).toContain("200");
  });
  it("shows failure", () => {
    const { container } = render(<WebhookTestResult success={false} statusCode={500} durationMs={100} verdict="❌ Error" responsePreview="" />);
    expect(container.textContent).toContain("Error");
  });
});
