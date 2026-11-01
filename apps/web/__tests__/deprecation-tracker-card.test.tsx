import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DeprecationTrackerCard from "../src/components/deprecation-tracker-card";

const deprecations = [
  {
    deprecation_id: "d1",
    resource: "GET /api/v1/users",
    sunset_date: "2027-01-01",
    replacement: "GET /api/v2/users",
    migration_progress: 75,
    usage_count: 25,
  },
  {
    deprecation_id: "d2",
    resource: "POST /api/v1/auth",
    sunset_date: "2027-06-01",
    replacement: "",
    migration_progress: 100,
    usage_count: 0,
  },
];

describe("DeprecationTrackerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <DeprecationTrackerCard deprecations={deprecations} appName="My App" />,
    );
    expect(container.textContent).toContain("Deprecations");
    expect(container.textContent).toContain("My App");
  });

  it("shows pending count", () => {
    const { container } = render(
      <DeprecationTrackerCard deprecations={deprecations} appName="App" />,
    );
    expect(container.textContent).toContain("1 pending");
  });

  it("shows all-migrated", () => {
    const migrated = [deprecations[1]];
    const { container } = render(<DeprecationTrackerCard deprecations={migrated} appName="App" />);
    expect(container.textContent).toContain("All migrated");
  });

  it("renders resource and sunset", () => {
    const { container } = render(
      <DeprecationTrackerCard deprecations={deprecations} appName="App" />,
    );
    expect(container.textContent).toContain("GET /api/v1/users");
    expect(container.textContent).toContain("sunset 2027-01-01");
  });

  it("shows replacement", () => {
    const { container } = render(
      <DeprecationTrackerCard deprecations={deprecations} appName="App" />,
    );
    expect(container.textContent).toContain("→ GET /api/v2/users");
  });

  it("shows migration progress", () => {
    const { container } = render(
      <DeprecationTrackerCard deprecations={deprecations} appName="App" />,
    );
    expect(container.textContent).toContain("75%");
  });

  it("shows empty state", () => {
    const { container } = render(<DeprecationTrackerCard deprecations={[]} appName="App" />);
    expect(container.textContent).toContain("No deprecations");
  });
});
