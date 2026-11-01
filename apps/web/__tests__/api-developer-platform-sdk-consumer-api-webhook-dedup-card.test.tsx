import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookDedupCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-dedup-card";

describe("WebhookDedupCard", () => {
  it("renders title and stats", () => {
    const { container } = render(<WebhookDedupCard />);
    expect(container.textContent).toContain("Webhook Dedup");
    expect(container.textContent).toContain("8.6%");
    expect(container.textContent).toContain("Dedup Rate");
  });

  it("shows total checked", () => {
    const { container } = render(<WebhookDedupCard />);
    expect(container.textContent).toContain("45,200 checked");
  });
});
