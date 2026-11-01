import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIDeprecationTrackerCard from "../src/components/api-developer-api-deprecation-tracker-card";

const deprecations = [
  { endpoint: "/api/v1/old", replacement: "/api/v2/new", days_until_sunset: 25, hit_count: 150, unique_consumer_count: 3 },
];

describe("APIDeveloperAPIDeprecationTrackerCard", () => {
  it("shows deprecation data", () => {
    const { container } = render(<APIDeveloperAPIDeprecationTrackerCard deprecations={deprecations} pastSunsetCount={1} appName="App" />);
    expect(container.textContent).toContain("Deprecation Tracker");
    expect(container.textContent).toContain("1 past sunset");
    expect(container.textContent).toContain("/api/v1/old");
    expect(container.textContent).toContain("25d left");
    expect(container.textContent).toContain("/api/v2/new");
    expect(container.textContent).toContain("150 hits");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIDeprecationTrackerCard deprecations={[]} pastSunsetCount={0} appName="App" />);
    expect(container.textContent).toContain("No deprecated endpoints");
  });
});
