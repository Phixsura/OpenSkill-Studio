import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiErrorBreakdown } from "@/components/api-error-breakdown";

describe("ApiErrorBreakdown", () => {
  it("renders breakdown", () => {
    const { container } = render(
      <ApiErrorBreakdown total={10} clientErrors={6} serverErrors={4}
        topEndpoint="/api/apps" byStatus={{ 404: 4, 422: 2, 500: 4 }}
        byType={{ not_found: 4, internal: 4, validation: 2 }} />
    );
    expect(container.textContent).toContain("API Errors");
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("4xx");
    expect(container.textContent).toContain("/api/apps");
    expect(container.textContent).toContain("500: 4");
  });
});
