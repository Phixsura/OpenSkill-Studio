import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthDashboard } from "@/components/health-dashboard";

describe("HealthDashboard", () => {
  const endpoints = [
    { name: "API", url: "https://api.example.com", healthy: true, status_code: 200, response_ms: 45 },
    { name: "Web", url: "https://web.example.com", healthy: true, status_code: 200, response_ms: 120 },
  ];
  it("renders endpoints", () => {
    const { container } = render(<HealthDashboard endpoints={endpoints} overall="healthy" healthy={2} unhealthy={0} />);
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("2↑");
  });
});
