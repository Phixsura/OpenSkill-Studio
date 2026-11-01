import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeliveryLog } from "@/components/delivery-log";

describe("DeliveryLog", () => {
  const deliveries = [
    { id: "d1", eventType: "app.installed", statusCode: 200, success: true, durationMs: 50, deliveredAt: "2026-01-01" },
    { id: "d2", eventType: "app.updated", statusCode: 500, success: false, durationMs: 3000, deliveredAt: "2026-01-02" },
  ];
  it("renders deliveries", () => {
    const { container } = render(<DeliveryLog deliveries={deliveries} successRate={50} avgDurationMs={1525} />);
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("50%");
  });
});
