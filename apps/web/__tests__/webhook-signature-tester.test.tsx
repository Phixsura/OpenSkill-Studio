import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookSignatureTester } from "@/components/webhook-signature-tester";

describe("WebhookSignatureTester", () => {
  it("renders form fields", () => {
    const { container, getByPlaceholderText } = render(<WebhookSignatureTester />);
    expect(container.textContent).toContain("Webhook Signature Tester");
    expect(getByPlaceholderText("whsec_...")).toBeDefined();
    expect(getByPlaceholderText("sha256=...")).toBeDefined();
  });

  it("disables verify when fields empty", () => {
    const { getByText } = render(<WebhookSignatureTester />);
    const btn = getByText("🔍 Verify Signature");
    expect(btn.hasAttribute("disabled")).toBe(true);
  });

  it("calls onVerify and shows result", () => {
    const onVerify = vi.fn().mockReturnValue(true);
    const { getByText, getByPlaceholderText, container } = render(
      <WebhookSignatureTester onVerify={onVerify} />
    );
    fireEvent.change(getByPlaceholderText("whsec_..."), { target: { value: "my-secret" } });
    fireEvent.change(getByPlaceholderText("sha256=..."), { target: { value: "sha256=abc123" } });
    fireEvent.click(getByText("🔍 Verify Signature"));
    expect(onVerify).toHaveBeenCalled();
    expect(container.textContent).toContain("valid");
  });

  it("generates a signature", () => {
    const { getByText, getByPlaceholderText } = render(<WebhookSignatureTester />);
    fireEvent.change(getByPlaceholderText("whsec_..."), { target: { value: "secret" } });
    fireEvent.click(getByText("Generate"));
    const sigInput = getByPlaceholderText("sha256=...") as HTMLInputElement;
    expect(sigInput.value).toContain("sha256=");
  });
});
