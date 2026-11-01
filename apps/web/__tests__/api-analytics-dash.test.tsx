import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiAnalyticsDash } from "@/components/api-analytics-dash";

describe("ApiAnalyticsDash", () => {
  it("renders", () => {
    const { container } = render(
      <ApiAnalyticsDash totalRequests={10000} uniqueEndpoints={5} peakHour={9}
        byMethod={{ GET: 7000, POST: 3000 }}
        topEndpoints={[
          { endpoint: "/users", count: 5000, errors: 10 },
          { endpoint: "/orders", count: 3000, errors: 50 },
        ]} />
    );
    expect(container.textContent).toContain("API Analytics");
    expect(container.textContent).toContain("10,000 reqs");
    expect(container.textContent).toContain("peak: 9:00");
    expect(container.textContent).toContain("GET: 7,000");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("50 err");
  });
});
