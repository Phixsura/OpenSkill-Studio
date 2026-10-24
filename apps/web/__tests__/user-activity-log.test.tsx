import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UserActivityLog } from "@/components/user-activity-log";

describe("UserActivityLog", () => {
  const activities = [
    { action: "login", label: "Logged in", icon: "🔑", target: "", timestamp: "2026-01-01T10:00:00Z", ip: "1.2.3.4" },
    { action: "create_app", label: "Created app", icon: "📦", target: "SuperApp", timestamp: "2026-01-01T10:05:00Z", ip: "" },
  ];
  it("renders activity log", () => {
    const { container } = render(<UserActivityLog activities={activities} activeDays={1} />);
    expect(container.textContent).toContain("Activity Log");
    expect(container.textContent).toContain("Logged in");
    expect(container.textContent).toContain("Created app");
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("1 active days");
  });
});
