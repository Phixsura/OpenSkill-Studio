import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookSecretCard } from "@/components/webhook-secret-card";

describe("WebhookSecretCard", () => {
  it("renders secret card", () => {
    const { container } = render(
      <WebhookSecretCard preview="whsec_abc12345••••" createdAt="2026-01-01"
        onRotate={vi.fn()} onReveal={() => "whsec_full_secret"} />
    );
    expect(container.textContent).toContain("Webhook Secret");
    expect(container.textContent).toContain("whsec_abc12345");
    expect(container.textContent).toContain("Rotate");
    expect(container.textContent).toContain("Reveal");
  });
});
