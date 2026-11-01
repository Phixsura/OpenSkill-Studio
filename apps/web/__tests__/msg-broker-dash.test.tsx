import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MsgBrokerDash } from "@/components/msg-broker-dash";

describe("MsgBrokerDash", () => {
  it("renders", () => {
    const { container } = render(
      <MsgBrokerDash totalDelivered={5000} totalPending={12}
        topics={[
          { name: "orders", subscribers: 3, pendingMessages: 5 },
          { name: "users", subscribers: 2, pendingMessages: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Message Broker");
    expect(container.textContent).toContain("5,000 delivered");
    expect(container.textContent).toContain("12 pending");
    expect(container.textContent).toContain("orders");
    expect(container.textContent).toContain("3 subs");
    expect(container.textContent).toContain("5 pending");
  });
});
