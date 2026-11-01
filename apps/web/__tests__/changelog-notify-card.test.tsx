import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChangelogNotifyCard from "../src/components/changelog-notify-card";

const deliveries = [
  { version: "2.0.0", channel: "email", recipient: "alice@example.com", success: true },
  { version: "2.0.0", channel: "slack", recipient: "#releases", success: true },
  { version: "1.5.0", channel: "webhook", recipient: "https://hooks.example.com", success: false },
];

describe("ChangelogNotifyCard", () => {
  it("renders header", () => {
    const { container } = render(
      <ChangelogNotifyCard deliveries={deliveries} totalDeliveries={50} appName="My App" />,
    );
    expect(container.textContent).toContain("Release Notifications");
  });

  it("shows total sent", () => {
    const { container } = render(
      <ChangelogNotifyCard deliveries={deliveries} totalDeliveries={50} appName="App" />,
    );
    expect(container.textContent).toContain("50 sent");
  });

  it("renders recipients and channels", () => {
    const { container } = render(
      <ChangelogNotifyCard deliveries={deliveries} totalDeliveries={0} appName="App" />,
    );
    expect(container.textContent).toContain("alice@example.com");
    expect(container.textContent).toContain("✉️");
    expect(container.textContent).toContain("💬");
  });

  it("shows success/failure", () => {
    const { container } = render(
      <ChangelogNotifyCard deliveries={deliveries} totalDeliveries={0} appName="App" />,
    );
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("✕");
  });

  it("shows empty state", () => {
    const { container } = render(
      <ChangelogNotifyCard deliveries={[]} totalDeliveries={0} appName="App" />,
    );
    expect(container.textContent).toContain("No notifications sent");
  });
});
