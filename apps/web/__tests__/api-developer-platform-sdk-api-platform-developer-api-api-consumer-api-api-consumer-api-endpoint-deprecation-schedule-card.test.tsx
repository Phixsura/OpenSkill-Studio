import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-endpoint-deprecation-schedule-card";

describe("EndpointDeprecationScheduleCard", () => {
  it("shows entries", () => {
    const entries = [
      { id: "e1", path: "/api/v1/users", status: "deprecated", deprecatedAt: "2026-06-01", sunsetAt: "2026-09-01", replacement: "/api/v2/users" },
    ];
    const { container } = render(<Card entries={entries} appName="App" />);
    expect(container.textContent).toContain("Deprecation Schedule");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("deprecated");
    expect(container.textContent).toContain("/api/v2/users");
  });
  it("shows empty", () => {
    const { container } = render(<Card entries={[]} appName="App" />);
    expect(container.textContent).toContain("No deprecations scheduled");
  });
});
