import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MaintenanceWindowCard from "../src/components/maintenance-window-card";

const windows = [
  {
    window_id: "w1",
    title: "DB Migration",
    status: "active" as const,
    start_at: new Date().toISOString(),
    end_at: new Date(Date.now() + 3600000).toISOString(),
    affected_services: ["db", "api"],
  },
  {
    window_id: "w2",
    title: "Security Patch",
    status: "scheduled" as const,
    start_at: new Date(Date.now() + 86400000).toISOString(),
    end_at: new Date(Date.now() + 90000000).toISOString(),
    affected_services: ["auth"],
  },
];

describe("MaintenanceWindowCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <MaintenanceWindowCard windows={windows} inMaintenance={true} appName="My App" />,
    );
    expect(container.textContent).toContain("Maintenance");
    expect(container.textContent).toContain("My App");
  });

  it("shows in-progress badge", () => {
    const { container } = render(
      <MaintenanceWindowCard windows={windows} inMaintenance={true} appName="App" />,
    );
    expect(container.textContent).toContain("In Progress");
  });

  it("shows window count when not in maintenance", () => {
    const { container } = render(
      <MaintenanceWindowCard windows={windows} inMaintenance={false} appName="App" />,
    );
    expect(container.textContent).toContain("2 windows");
  });

  it("renders window titles", () => {
    const { container } = render(
      <MaintenanceWindowCard windows={windows} inMaintenance={false} appName="App" />,
    );
    expect(container.textContent).toContain("DB Migration");
    expect(container.textContent).toContain("Security Patch");
  });

  it("shows affected services", () => {
    const { container } = render(
      <MaintenanceWindowCard windows={windows} inMaintenance={false} appName="App" />,
    );
    expect(container.textContent).toContain("db");
    expect(container.textContent).toContain("api");
  });

  it("shows empty state", () => {
    const { container } = render(
      <MaintenanceWindowCard windows={[]} inMaintenance={false} appName="App" />,
    );
    expect(container.textContent).toContain("No maintenance windows");
  });
});
