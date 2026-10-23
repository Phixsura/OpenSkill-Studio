import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookTesterUi } from "@/components/webhook-tester-ui";

describe("WebhookTesterUi", () => {
  it("renders tester", () => {
    const onTest = vi.fn();
    const { container, getByText } = render(
      <WebhookTesterUi testing={false} onTest={onTest}
        result={{ success: true, statusCode: 200, latencyMs: 150, grade: "A", issues: [], isJson: true }} />
    );
    expect(container.textContent).toContain("Webhook Tester");
    expect(container.textContent).toContain("Success");
    expect(container.textContent).toContain("Grade: A");
    expect(container.textContent).toContain("150ms");
    fireEvent.click(getByText("Send Test Event"));
    expect(onTest).toHaveBeenCalled();
  });
});
