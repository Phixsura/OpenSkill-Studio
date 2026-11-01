import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-maintenance-window-card";

describe("EndpointMaintenanceWindowCard", () => {
  it("shows windows", () => {
    const windows = [{ id: "w1", path: "/api/users", startsAt: "12:00", endsAt: "14:00", reason: "Deploy v2", status: "scheduled" }];
    const { container } = render(<Card windows={windows} appName="App" />);
    expect(container.textContent).toContain("Maintenance Windows");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("scheduled");
    expect(container.textContent).toContain("Deploy v2");
  });
  it("shows empty", () => {
    const { container } = render(<Card windows={[]} appName="App" />);
    expect(container.textContent).toContain("No maintenance scheduled");
  });
});
