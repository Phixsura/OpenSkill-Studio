import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIPlatformAnnouncementCard from "../src/components/api-platform-announcement-card";

const anns = [{ announcement_id: "a1", title: "Maintenance", body: "Scheduled downtime tonight", severity: "warning", active: true }];

describe("APIPlatformAnnouncementCard", () => {
  it("shows announcements", () => {
    const { container } = render(<APIPlatformAnnouncementCard announcements={anns} appName="App" />);
    expect(container.textContent).toContain("Announcements");
    expect(container.textContent).toContain("Maintenance");
    expect(container.textContent).toContain("Scheduled downtime");
  });
  it("shows empty", () => {
    const { container } = render(<APIPlatformAnnouncementCard announcements={[]} appName="App" />);
    expect(container.textContent).toContain("No active announcements");
  });
});
