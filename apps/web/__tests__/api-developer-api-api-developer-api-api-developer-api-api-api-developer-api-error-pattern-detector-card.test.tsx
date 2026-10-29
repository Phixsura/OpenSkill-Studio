import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiErrorPatternDetectorCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-developer-api-error-pattern-detector-card";

const patterns = [{ pattern_id: "ep-1", error_code: "RATE_LIMITED", endpoint: "/api/users", occurrence_count: 150, severity: "critical", affected_consumer_count: 12 }];

describe("Card", () => {
  it("shows error patterns", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiErrorPatternDetectorCard patterns={patterns} criticalCount={1} appName="App" />);
    expect(container.textContent).toContain("Error Patterns");
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("RATE_LIMITED");
    expect(container.textContent).toContain("150×");
    expect(container.textContent).toContain("12 consumers");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiErrorPatternDetectorCard patterns={[]} criticalCount={0} appName="App" />);
    expect(container.textContent).toContain("No error patterns");
  });
});
