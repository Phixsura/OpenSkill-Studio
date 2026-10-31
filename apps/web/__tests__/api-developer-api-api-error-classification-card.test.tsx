import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiErrorClassificationCard from "../src/components/api-developer-api-api-error-classification-card";

const errors = [
  { error_code: "UNAUTHORIZED", category: "auth", count: 50, endpoints_affected_count: 3 },
  { error_code: "INTERNAL_ERROR", category: "server", count: 10, endpoints_affected_count: 1 },
];

describe("APIDeveloperAPIApiErrorClassificationCard", () => {
  it("shows error classification", () => {
    const { container } = render(<APIDeveloperAPIApiErrorClassificationCard errors={errors} totalErrors={60} categoryBreakdown={{ auth: 50, server: 10 }} appName="App" />);
    expect(container.textContent).toContain("Error Classification");
    expect(container.textContent).toContain("60");
    expect(container.textContent).toContain("auth: 50");
    expect(container.textContent).toContain("UNAUTHORIZED");
    expect(container.textContent).toContain("50×");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiErrorClassificationCard errors={[]} totalErrors={0} categoryBreakdown={{}} appName="App" />);
    expect(container.textContent).toContain("No errors");
  });
});
