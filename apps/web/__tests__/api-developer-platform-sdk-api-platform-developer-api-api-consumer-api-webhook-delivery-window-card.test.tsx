import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-webhook-delivery-window-card";

describe("DeliveryWindowCard", () => {
  it("shows windows", () => {
    const windows = [{ consumer_id: "c1", start_hour: 9, end_hour: 17, timezone: "UTC", days: ["mon", "fri"], buffer: true }];
    const { container } = render(<Card windows={windows} appName="App" />);
    expect(container.textContent).toContain("Delivery Windows");
    expect(container.textContent).toContain("09:00–17:00");
    expect(container.textContent).toContain("mon");
    expect(container.textContent).toContain("buffer");
  });
  it("shows empty", () => {
    const { container } = render(<Card windows={[]} appName="App" />);
    expect(container.textContent).toContain("No delivery windows");
  });
});
