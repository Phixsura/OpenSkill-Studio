import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import NotifPrefsCard from "../src/components/api-developer-platform-sdk-consumer-api-notif-prefs-card";

describe("NotifPrefsCard", () => {
  it("renders title and events", () => {
    const { container } = render(<NotifPrefsCard />);
    expect(container.textContent).toContain("Notification Preferences");
    expect(container.textContent).toContain("Incidents");
    expect(container.textContent).toContain("Security");
  });

  it("shows channels and active count", () => {
    const { container } = render(<NotifPrefsCard />);
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("slack");
    expect(container.textContent).toContain("4/5 event types active");
  });
});
