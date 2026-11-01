import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WhDeliveryLogPanel } from "@/components/wh-delivery-log-panel";
describe("WhDeliveryLogPanel", () => {
  it("renders", () => {
    const { container } = render(
      <WhDeliveryLogPanel failureRate={33.3} total={3}
        deliveries={[
          { webhookId: "w1", url: "https://a.com/hook", statusCode: 200, durationMs: 150, success: true },
          { webhookId: "w1", url: "https://a.com/hook", statusCode: 500, durationMs: 200, success: false },
        ]} />
    );
    expect(container.textContent).toContain("Delivery Log");
    expect(container.textContent).toContain("33.3% failure");
    expect(container.textContent).toContain("3 total");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });
});
