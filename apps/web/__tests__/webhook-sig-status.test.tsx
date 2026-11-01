import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WebhookSigStatus } from "@/components/webhook-sig-status";

describe("WebhookSigStatus", () => {
  it("renders", () => {
    const { container } = render(
      <WebhookSigStatus verified={950} failed={50} total={1000} algorithm="sha256" />
    );
    expect(container.textContent).toContain("Webhook Signatures");
    expect(container.textContent).toContain("sha256");
    expect(container.textContent).toContain("1000 checked");
    expect(container.textContent).toContain("950");
    expect(container.textContent).toContain("50");
  });
});
