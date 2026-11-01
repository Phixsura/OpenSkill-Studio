import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WhQueueMgrPanel } from "@/components/wh-queue-mgr-panel";
describe("WhQueueMgrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <WhQueueMgrPanel totalQueued={50} processed={10000}
        queues={[
          { subscriberId: "sub-1", depth: 30 },
          { subscriberId: "sub-2", depth: 20 },
        ]} />
    );
    expect(container.textContent).toContain("Webhook Queues");
    expect(container.textContent).toContain("50 queued");
    expect(container.textContent).toContain("10,000 processed");
    expect(container.textContent).toContain("sub-1");
    expect(container.textContent).toContain("30 pending");
  });
});
