import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeadLetterQueue } from "@/components/dead-letter-queue";

const ITEMS = [{ eventId: "e1", eventType: "app.installed", url: "u", error: "timeout", attempts: 5, deadAt: "now" }];

describe("DeadLetterQueue", () => {
  it("shows items", () => {
    const { container } = render(<DeadLetterQueue items={ITEMS} />);
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("timeout");
  });
  it("empty state", () => {
    const { container } = render(<DeadLetterQueue items={[]} />);
    expect(container.textContent).toContain("No dead letters");
  });
  it("has retry button", () => {
    const { container } = render(<DeadLetterQueue items={ITEMS} onRetry={vi.fn()} />);
    expect(container.textContent).toContain("Retry");
  });
  it("has purge button", () => {
    const { container } = render(<DeadLetterQueue items={ITEMS} onPurge={vi.fn()} />);
    expect(container.textContent).toContain("Purge");
  });
});
