import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiExplorerPage } from "@/components/api-explorer-page";

describe("ApiExplorerPage", () => {
  const endpoints = [
    { method: "GET", path: "/api/v1/apps", fullUrl: "https://api.x.dev/api/v1/apps", summary: "List apps", auth: true, tag: "Apps" },
  ];
  it("renders explorer", () => {
    const { container } = render(
      <ApiExplorerPage endpoints={endpoints} tags={["Apps"]} baseUrl="https://api.x.dev" onFilter={vi.fn()} />
    );
    expect(container.textContent).toContain("API Explorer");
    expect(container.textContent).toContain("/api/v1/apps");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("Apps");
  });
});
