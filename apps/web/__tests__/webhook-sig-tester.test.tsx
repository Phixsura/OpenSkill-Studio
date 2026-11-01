import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookSigTester } from "@/components/webhook-sig-tester";

describe("WebhookSigTester", () => {
  it("renders tester", () => {
    const { container } = render(
      <WebhookSigTester onSign={vi.fn()} onVerify={vi.fn()}
        result={{ valid: true }} />
    );
    expect(container.textContent).toContain("Webhook Signatures");
    expect(container.textContent).toContain("Sign");
    expect(container.textContent).toContain("Verify");
    expect(container.textContent).toContain("Valid");
  });
});
