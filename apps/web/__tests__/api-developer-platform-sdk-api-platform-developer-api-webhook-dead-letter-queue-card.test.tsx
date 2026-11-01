import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-webhook-dead-letter-queue-card";

describe("DLQCard", () => {
  it("shows entries", () => {
    const entries = [{ entry_id: "e1", consumer_id: "c1", reason: "timeout", attempts: 5, last_status_code: 500, requeued: false }];
    const { container } = render(<Card entries={entries} totalCount={1} reasonCounts={{ timeout: 1 }} appName="App" />);
    expect(container.textContent).toContain("Dead Letter Queue");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("timeout");
  });
  it("shows empty", () => {
    const { container } = render(<Card entries={[]} totalCount={0} reasonCounts={{}} appName="App" />);
    expect(container.textContent).toContain("Queue empty");
  });
});
