import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookSigPanel } from "@/components/webhook-sig-panel";

const mockProviders = [
  { provider: "github", headerName: "X-Hub-Signature-256", configured: true },
  { provider: "stripe", headerName: "Stripe-Signature", configured: false },
  { provider: "slack", headerName: "X-Slack-Signature", configured: true },
];

describe("WebhookSigPanel", () => {
  it("renders providers", () => {
    const { container } = render(<WebhookSigPanel providers={mockProviders} />);
    expect(container.textContent).toContain("github");
    expect(container.textContent).toContain("X-Hub-Signature-256");
  });

  it("calls onConfigure", () => {
    const onConfigure = vi.fn();
    const { getAllByText } = render(<WebhookSigPanel providers={mockProviders} onConfigure={onConfigure} />);
    fireEvent.click(getAllByText("Configure")[0]);
    expect(onConfigure).toHaveBeenCalledWith("stripe");
  });

  it("calls onTest for configured", () => {
    const onTest = vi.fn();
    const { getAllByText } = render(<WebhookSigPanel providers={mockProviders} onTest={onTest} />);
    fireEvent.click(getAllByText("Test")[0]);
    expect(onTest).toHaveBeenCalledWith("github");
  });
});
