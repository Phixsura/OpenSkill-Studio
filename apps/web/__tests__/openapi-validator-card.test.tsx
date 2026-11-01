import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import OpenAPIValidatorCard from "../src/components/openapi-validator-card";

const endpoints = [
  { method: "GET", path: "/api/users", compliance_pct: 100, total_checks: 50, last_violations: [] },
  {
    method: "POST",
    path: "/api/orders",
    compliance_pct: 85,
    total_checks: 20,
    last_violations: ["Missing 'id' field", "Wrong type for 'total'"],
  },
];

describe("OpenAPIValidatorCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<OpenAPIValidatorCard endpoints={endpoints} appName="My App" />);
    expect(container.textContent).toContain("API Contract");
    expect(container.textContent).toContain("My App");
  });

  it("shows failing count", () => {
    const { container } = render(<OpenAPIValidatorCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("1 failing");
  });

  it("shows all-compliant", () => {
    const { container } = render(<OpenAPIValidatorCard endpoints={[endpoints[0]]} appName="App" />);
    expect(container.textContent).toContain("All compliant");
  });

  it("renders methods and paths", () => {
    const { container } = render(<OpenAPIValidatorCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("POST");
  });

  it("shows compliance percentages", () => {
    const { container } = render(<OpenAPIValidatorCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("85%");
  });

  it("shows violations", () => {
    const { container } = render(<OpenAPIValidatorCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("Missing");
  });

  it("shows empty state", () => {
    const { container } = render(<OpenAPIValidatorCard endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No endpoints validated");
  });
});
