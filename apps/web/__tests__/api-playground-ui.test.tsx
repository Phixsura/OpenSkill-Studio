import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiPlaygroundUI } from "@/components/api-playground-ui";

const mockHistory = [
  { id: "e1", method: "GET", path: "/api/v1/health", statusCode: 200,
    body: '{"status":"ok"}', latencyMs: 12, assertionsPassed: 2, assertionsFailed: 0 },
  { id: "e2", method: "POST", path: "/api/v1/extensions", statusCode: 201,
    body: '{"id":"new"}', latencyMs: 45, assertionsPassed: 1, assertionsFailed: 1 },
];

describe("ApiPlaygroundUI", () => {
  it("renders playground with method selector", () => {
    const { container } = render(
      <ApiPlaygroundUI history={mockHistory} variables={{ ext_id: "ext-1" }} />
    );
    expect(container.textContent).toContain("API Playground");
    expect(container.querySelector("select")).toBeDefined();
  });

  it("calls onExecute", () => {
    const onExecute = vi.fn();
    const { getByText } = render(
      <ApiPlaygroundUI history={[]} variables={{}} onExecute={onExecute} />
    );
    fireEvent.click(getByText("Send"));
    expect(onExecute).toHaveBeenCalledWith("GET", "/api/v1/", "");
  });

  it("shows history with status", () => {
    const { getByText, container } = render(
      <ApiPlaygroundUI history={mockHistory} variables={{}} />
    );
    fireEvent.click(getByText("History (2)"));
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("12ms");
  });

  it("shows variables", () => {
    const { getByText, container } = render(
      <ApiPlaygroundUI history={[]} variables={{ ext_id: "ext-1", token: "abc" }} />
    );
    fireEvent.click(getByText("Variables"));
    expect(container.textContent).toContain("{{ext_id}}");
    expect(container.textContent).toContain("ext-1");
  });
});
