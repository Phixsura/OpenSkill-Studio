import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-api-changelog-subscription-card";

describe("ChangelogSubscriptionCard", () => {
  it("shows subscriptions", () => {
    const subs = [{ consumer_id: "c1", channels: ["email", "webhook"], active: true, notifications_sent: 42 }];
    const { container } = render(<Card subscriptions={subs} activeCount={1} appName="App" />);
    expect(container.textContent).toContain("Changelog Subs");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("42 sent");
  });
  it("shows empty", () => {
    const { container } = render(<Card subscriptions={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No subscriptions");
  });
});
