import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIHealthCheckCard from "../src/components/api-developer-api-health-check-card";

const checks = [
  { check_name: "Database", status: "pass", message: "OK", duration_ms: 5 },
  { check_name: "Cache", status: "fail", message: "Timeout", duration_ms: 3000 },
];

describe("APIDeveloperAPIHealthCheckCard", () => {
  it("shows checks", () => {
    const { container } = render(<APIDeveloperAPIHealthCheckCard checks={checks} allPassing={false} appName="App" />);
    expect(container.textContent).toContain("Health Checks");
    expect(container.textContent).toContain("Issues detected");
    expect(container.textContent).toContain("Database");
    expect(container.textContent).toContain("Cache");
  });
  it("shows all passing", () => {
    const { container } = render(<APIDeveloperAPIHealthCheckCard checks={[checks[0]]} allPassing={true} appName="App" />);
    expect(container.textContent).toContain("All passing");
  });
});
