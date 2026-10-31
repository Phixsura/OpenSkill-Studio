import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NotificationFeed } from "@/components/notification-feed";

describe("NotificationFeed", () => {
  it("renders feed", () => {
    const { container } = render(
      <NotificationFeed total={5} notifications={[
        { recipient: "u1", channel: "email", title: "Deploy Done", body: "v2.0 deployed", priority: "normal", status: "delivered" },
        { recipient: "u2", channel: "push", title: "Alert", body: "CPU high", priority: "high", status: "delivered" },
      ]} />
    );
    expect(container.textContent).toContain("Notifications");
    expect(container.textContent).toContain("5 sent");
    expect(container.textContent).toContain("Deploy Done");
    expect(container.textContent).toContain("Alert");
    expect(container.textContent).toContain("high");
  });
});
