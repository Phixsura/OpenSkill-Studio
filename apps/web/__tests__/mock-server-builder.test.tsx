import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MockServerBuilder } from "@/components/mock-server-builder";

describe("MockServerBuilder", () => {
  const endpoints = [
    { mock_id: "m1", path: "/users", method: "GET", status_code: 200, url: "https://mock.dev/users", delay_ms: 0 },
  ];
  it("renders", () => {
    const { container } = render(
      <MockServerBuilder collectionName="User API" baseUrl="https://mock.dev"
        endpoints={endpoints} onAdd={vi.fn()} onDelete={vi.fn()} onCopyUrl={vi.fn()} />
    );
    expect(container.textContent).toContain("User API");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/users");
  });
  it("delete", () => {
    const fn = vi.fn();
    const { container } = render(
      <MockServerBuilder collectionName="X" baseUrl="x" endpoints={endpoints}
        onAdd={vi.fn()} onDelete={fn} onCopyUrl={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "×")!);
    expect(fn).toHaveBeenCalledWith("m1");
  });
});
