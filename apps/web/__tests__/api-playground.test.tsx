import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiPlayground } from "@/components/api-playground";

describe("ApiPlayground", () => {
  it("renders playground", () => {
    const { container } = render(
      <ApiPlayground onSend={vi.fn()} history={[
        { method: "GET", path: "/api/users", status: 200, responseMs: 42 },
        { method: "POST", path: "/api/data", status: 201, responseMs: 85 },
      ]} />
    );
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("Send");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("42ms");
  });
});
