import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import NotificationPreferenceCard from "../src/components/notification-preference-card";

const pref = {
  channels: { email: true, push: true, in_app: true, sms: false },
  muted_categories: ["marketing", "promotions"],
  global_mute: false,
  quiet_hours_start: 22,
  quiet_hours_end: 7,
};

describe("NotificationPreferenceCard", () => {
  it("renders header with user id", () => {
    const { container } = render(
      <NotificationPreferenceCard pref={pref} userId="user-42" appName="My App" />,
    );
    expect(container.textContent).toContain("Notifications");
    expect(container.textContent).toContain("user-42");
  });

  it("shows enabled channel count", () => {
    const { container } = render(
      <NotificationPreferenceCard pref={pref} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("3 channels on");
  });

  it("shows global mute badge", () => {
    const mutedPref = { ...pref, global_mute: true };
    const { container } = render(
      <NotificationPreferenceCard pref={mutedPref} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("Muted");
  });

  it("renders channel badges", () => {
    const { container } = render(
      <NotificationPreferenceCard pref={pref} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("sms");
  });

  it("shows muted categories", () => {
    const { container } = render(
      <NotificationPreferenceCard pref={pref} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("marketing");
    expect(container.textContent).toContain("promotions");
  });

  it("shows quiet hours", () => {
    const { container } = render(
      <NotificationPreferenceCard pref={pref} userId="u1" appName="App" />,
    );
    expect(container.textContent).toContain("22:00");
    expect(container.textContent).toContain("7:00");
  });
});
