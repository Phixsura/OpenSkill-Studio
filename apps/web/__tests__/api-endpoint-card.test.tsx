import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiEndpointCard } from "@/components/api-endpoint-card";

describe("ApiEndpointCard", () => {
  it("shows method and path", () => {
    const { container } = render(<ApiEndpointCard method="GET" path="/api/v1/cohorts" summary="List cohorts" />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/v1/cohorts");
  });

  it("shows summary", () => {
    const { container } = render(<ApiEndpointCard method="POST" path="/x" summary="Create item" />);
    expect(container.textContent).toContain("Create item");
  });

  it("shows scopes", () => {
    const { container } = render(<ApiEndpointCard method="GET" path="/x" summary="X" scopes={["read:cohorts"]} />);
    expect(container.textContent).toContain("read:cohorts");
  });

  it("colors methods", () => {
    const { container } = render(<ApiEndpointCard method="DELETE" path="/x" summary="X" />);
    expect(container.querySelector("[class*='red']")).toBeTruthy();
  });
});
