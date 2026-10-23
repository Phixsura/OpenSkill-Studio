import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EndpointTester } from "@/components/endpoint-tester";

describe("EndpointTester", () => {
  const results = [
    { url: "https://api.example.com/v1/apps", method: "GET", pass: true, actualStatus: 200, responseMs: 45 },
    { url: "https://api.example.com/v1/bad", method: "POST", pass: false, actualStatus: 500, responseMs: 120 },
  ];
  it("renders test results", () => {
    const { container } = render(
      <EndpointTester results={results} passed={1} failed={1} allPass={false} avgResponseMs={82} />
    );
    expect(container.textContent).toContain("/v1/apps");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("1✓ 1✗");
  });
});
