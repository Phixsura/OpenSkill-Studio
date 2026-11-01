import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeliveryStatsCard } from "@/components/delivery-stats-card";

describe("DeliveryStatsCard", () => {
  it("renders stats", () => {
    const { container } = render(
      <DeliveryStatsCard total={100} success={95} failed={5} successDisplay="95.0%"
        avgLatencyMs={180} retryCount={3} health="good" byStatus={{ 200: 95, 500: 5 }} />
    );
    expect(container.textContent).toContain("Delivery Stats");
    expect(container.textContent).toContain("95.0%");
    expect(container.textContent).toContain("good");
    expect(container.textContent).toContain("200: 95");
    expect(container.textContent).toContain("500: 5");
    expect(container.textContent).toContain("3 retries");
  });
});
