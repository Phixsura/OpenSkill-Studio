import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKDeveloperPortalAnnouncementCard from "../src/components/api-developer-platform-sdk-developer-portal-announcement-card";

const announcements = [
  { announcement_id: "a1", title: "Scheduled Maintenance", body: "API will be down for 30min", severity: "maintenance", views: 500 },
];

describe("Card", () => {
  it("shows announcements", () => {
    const { container } = render(<APIDeveloperPlatformSDKDeveloperPortalAnnouncementCard announcements={announcements} appName="App" />);
    expect(container.textContent).toContain("Announcements");
    expect(container.textContent).toContain("Scheduled Maintenance");
    expect(container.textContent).toContain("API will be down");
    expect(container.textContent).toContain("500 views");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKDeveloperPortalAnnouncementCard announcements={[]} appName="App" />);
    expect(container.textContent).toContain("No announcements");
  });
});
