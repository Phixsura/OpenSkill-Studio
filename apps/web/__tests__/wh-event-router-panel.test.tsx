import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WhEventRouterPanel } from "@/components/wh-event-router-panel";
describe("WhEventRouterPanel", () => {
  it("renders", () => {
    const { container } = render(
      <WhEventRouterPanel totalDelivered={5000}
        routes={[
          { eventType: "order.created", handlers: 3 },
          { eventType: "user.signup", handlers: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Event Router");
    expect(container.textContent).toContain("5,000 delivered");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("3 handlers");
  });
});
