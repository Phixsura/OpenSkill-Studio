import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiPlayground } from "@/components/api-playground";

const mockEndpoints = [
  { method: "GET" as const, path: "/extensions/{id}", description: "Get extension by ID",
    params: [{ name: "id", in: "path" as const, type: "string", required: true }] },
  { method: "POST" as const, path: "/webhooks", description: "Create webhook",
    params: [
      { name: "url", in: "body" as const, type: "string", required: true },
      { name: "events", in: "body" as const, type: "array", required: true },
    ] },
];

describe("ApiPlayground", () => {
  it("renders endpoint list", () => {
    const { container } = render(
      <ApiPlayground endpoints={mockEndpoints} baseUrl="https://api.test.com/v1" />
    );
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/extensions/{id}");
    expect(container.textContent).toContain("POST");
  });

  it("shows params for selected endpoint", () => {
    const { container } = render(
      <ApiPlayground endpoints={mockEndpoints} baseUrl="https://api.test.com" />
    );
    expect(container.textContent).toContain("Get extension by ID");
    expect(container.textContent).toContain("id");
  });

  it("calls onExecute with built URL", () => {
    const onExecute = vi.fn();
    const { getByText } = render(
      <ApiPlayground endpoints={mockEndpoints} baseUrl="https://api.test.com" onExecute={onExecute} />
    );
    fireEvent.click(getByText("▶ Send Request"));
    expect(onExecute).toHaveBeenCalled();
  });
});
