import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookQueueCard from "../src/components/webhook-queue-card";

const stats = { queued: 5, delivering: 2, delivered: 100, failed: 3, dead_letter: 1 };

describe("WebhookQueueCard", () => {
  it("renders header and total", () => {
    const { container } = render(
      <WebhookQueueCard stats={stats} queueDepth={5} deadLetterCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("Webhook Queue");
    expect(container.textContent).toContain("111 total");
  });

  it("shows queue depth", () => {
    const { container } = render(
      <WebhookQueueCard stats={stats} queueDepth={5} deadLetterCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("queued");
  });

  it("shows delivered count", () => {
    const { container } = render(
      <WebhookQueueCard stats={stats} queueDepth={5} deadLetterCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("delivered");
  });

  it("shows dead letter alert", () => {
    const { container } = render(
      <WebhookQueueCard stats={stats} queueDepth={5} deadLetterCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("1 dead letters");
  });
});
