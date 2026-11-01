import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIErrorAnalyticsCard from "../src/components/api-developer-api-error-analytics-card";

const errors = { total_errors: 500, unique_error_codes: 15, top_error_code: "AUTH_FAIL", top_error_count: 200, error_rate_trend: "decreasing", most_affected_endpoint: "/api/auth" };

describe("APIDeveloperAPIErrorAnalyticsCard", () => {
  it("shows error analytics", () => {
    const { container } = render(<APIDeveloperAPIErrorAnalyticsCard errors={errors} appName="App" />);
    expect(container.textContent).toContain("Error Analytics");
    expect(container.textContent).toContain("500 errors");
    expect(container.textContent).toContain("AUTH_FAIL");
    expect(container.textContent).toContain("decreasing");
  });
});
