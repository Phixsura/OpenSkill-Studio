import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiDocViewer } from "@/components/api-doc-viewer";

const mockEndpoints = [
  { method: "get", path: "/api/v1/items", summary: "List items",
    tags: ["items"], authRequired: true, deprecated: false,
    params: [{ name: "page", location: "query", type: "integer", required: false }] },
  { method: "post", path: "/api/v1/items", summary: "Create item",
    tags: ["items"], authRequired: true, deprecated: false, params: [] },
  { method: "get", path: "/api/v1/health", summary: "Health check",
    tags: ["system"], authRequired: false, deprecated: false, params: [] },
];

describe("ApiDocViewer", () => {
  it("renders endpoints", () => {
    const { container } = render(
      <ApiDocViewer endpoints={mockEndpoints} title="My API" version="2.0.0" />
    );
    expect(container.textContent).toContain("My API");
    expect(container.textContent).toContain("/api/v1/items");
    expect(container.textContent).toContain("List items");
  });

  it("filters by tag", () => {
    const { getByText, container } = render(
      <ApiDocViewer endpoints={mockEndpoints} title="API" version="1.0" />
    );
    fireEvent.click(getByText("system"));
    expect(container.textContent).toContain("/api/v1/health");
    expect(container.textContent).not.toContain("List items");
  });

  it("expands to show params", () => {
    const { container } = render(
      <ApiDocViewer endpoints={mockEndpoints} title="API" version="1.0" />
    );
    const row = container.querySelector("[class*='cursor-pointer']");
    if (row) fireEvent.click(row);
    expect(container.textContent).toContain("page");
    expect(container.textContent).toContain("query");
  });

  it("calls onTryIt", () => {
    const onTryIt = vi.fn();
    const { container, getByText } = render(
      <ApiDocViewer endpoints={mockEndpoints} title="API" version="1.0" onTryIt={onTryIt} />
    );
    const row = container.querySelector("[class*='cursor-pointer']");
    if (row) fireEvent.click(row);
    fireEvent.click(getByText("Try It"));
    expect(onTryIt).toHaveBeenCalledWith("get", "/api/v1/items");
  });
});
