import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MaintenanceWindowCard from "../src/components/maintenance-window-card";

const windows = [
  {
    window_id: "w1",
    title: "DB Upgrade",
    status: "active" as const,
    duration_minutes: 60,
    affected_services: ["db", "api"],
    message: "",
  },
  {
    window_id: "w2",
    title: "Cache Flush",
    status: "scheduled" as const,
    duration_minutes: 15,
    affected_services: ["cache"],
    message: "",
  },
];

describe("MaintenanceWindowCard", () => {
  it("renders header and maintenance banner", () => {
    const { container } = render(
      <MaintenanceWindowCard windows={windows} isInMaintenance={true} appName="App" />,
    );
    expect(container.textContent).toContain("Maintenance Windows");
    expect(container.textContent).toContain("In Maintenance");
  });

  it("shows window titles and status", () => {
    const { container } = render(
      <MaintenanceWindowCard windows={windows} isInMaintenance={false} appName="App" />,
    );
    expect(container.textContent).toContain("DB Upgrade");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("scheduled");
  });

  it("shows duration and services", () => {
    const { container } = render(
      <MaintenanceWindowCard windows={windows} isInMaintenance={false} appName="App" />,
    );
    expect(container.textContent).toContain("60 min");
    expect(container.textContent).toContain("db, api");
  });

  it("shows empty state", () => {
    const { container } = render(
      <MaintenanceWindowCard windows={[]} isInMaintenance={false} appName="App" />,
    );
    expect(container.textContent).toContain("No maintenance windows");
  });
});
