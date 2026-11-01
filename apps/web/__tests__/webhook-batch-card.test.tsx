import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookBatchCard from "../src/components/webhook-batch-card";

const batches = [
  {
    batch_id: "b1",
    destination: "https://hooks.example.com/a",
    event_count: 5,
    flushed: true,
    delivered: true,
  },
  {
    batch_id: "b2",
    destination: "https://hooks.example.com/b",
    event_count: 3,
    flushed: true,
    delivered: false,
  },
  {
    batch_id: "b3",
    destination: "https://hooks.example.com/c",
    event_count: 1,
    flushed: false,
    delivered: false,
  },
];

describe("WebhookBatchCard", () => {
  it("renders header and counts", () => {
    const { container } = render(
      <WebhookBatchCard batches={batches} pendingCount={1} appName="App" />,
    );
    expect(container.textContent).toContain("Webhook Batches");
    expect(container.textContent).toContain("3 batches");
    expect(container.textContent).toContain("1 pending");
  });

  it("shows event counts", () => {
    const { container } = render(
      <WebhookBatchCard batches={batches} pendingCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("5 events");
    expect(container.textContent).toContain("3 events");
  });

  it("shows destinations", () => {
    const { container } = render(
      <WebhookBatchCard batches={batches} pendingCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("hooks.example.com");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookBatchCard batches={[]} pendingCount={0} appName="App" />);
    expect(container.textContent).toContain("No batches");
  });
});
