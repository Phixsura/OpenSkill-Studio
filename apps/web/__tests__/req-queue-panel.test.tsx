import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqQueuePanel } from "@/components/req-queue-panel";

describe("ReqQueuePanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqQueuePanel queueSize={15} dlqSize={3} processed={10000} maxRetries={3} />
    );
    expect(container.textContent).toContain("Request Queue");
    expect(container.textContent).toContain("max 3 retries");
    expect(container.textContent).toContain("15");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("3");
  });
});
