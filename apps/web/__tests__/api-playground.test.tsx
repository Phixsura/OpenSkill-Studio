import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiPlayground } from "@/components/api-playground";

const EPS = [{ method: "GET", path: "/api/v1/apps", description: "List apps", auth: true }];

describe("ApiPlayground", () => {
  it("shows endpoints", () => {
    const { container } = render(<ApiPlayground endpoints={EPS} onExecute={vi.fn()} />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/v1/apps");
  });
  it("has title", () => {
    const { container } = render(<ApiPlayground endpoints={[]} onExecute={vi.fn()} />);
    expect(container.textContent).toContain("Playground");
  });
});
