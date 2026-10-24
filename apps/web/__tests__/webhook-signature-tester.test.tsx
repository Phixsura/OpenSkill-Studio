import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookSignatureTester } from "@/components/webhook-signature-tester";

describe("WebhookSignatureTester", () => {
  it("renders", () => {
    const { container } = render(<WebhookSignatureTester onVerify={vi.fn(() => ({ valid: true }))} />);
    expect(container.textContent).toContain("Signature Tester");
    expect(container.querySelector("textarea")).toBeTruthy();
    expect(container.textContent).toContain("Verify");
  });
  it("verify valid", () => {
    const fn = vi.fn(() => ({ valid: true }));
    const { container } = render(<WebhookSignatureTester onVerify={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Verify")!);
    expect(fn).toHaveBeenCalled();
    expect(container.textContent).toContain("✅ Valid signature");
  });
});
