import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WhSubMgrPanel } from "@/components/wh-sub-mgr-panel";
describe("WhSubMgrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <WhSubMgrPanel active={2} totalDeliveries={500}
        subscriptions={[
          { id: "s1", url: "https://a.com/hook", events: ["order.created"], deliveries: 300 },
          { id: "s2", url: "https://b.com/hook", events: ["order.created", "order.paid"], deliveries: 200 },
        ]} />
    );
    expect(container.textContent).toContain("Webhook Subscriptions");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("500 deliveries");
    expect(container.textContent).toContain("a.com/hook");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("300 sent");
  });
});
