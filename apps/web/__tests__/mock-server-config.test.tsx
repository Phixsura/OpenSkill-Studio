import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MockServerConfig } from "@/components/mock-server-config";

describe("MockServerConfig", () => {
  it("renders mocks", () => {
    const onAdd = vi.fn();
    const { container, getByText } = render(
      <MockServerConfig totalHits={5} onAdd={onAdd} mocks={[
        { method: "GET", path: "/api/users", hits: 3 },
        { method: "POST", path: "/api/users", hits: 2 },
      ]} />
    );
    expect(container.textContent).toContain("Mock Server");
    expect(container.textContent).toContain("5 total hits");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("POST");
    fireEvent.click(getByText("+ Add Mock Endpoint"));
    expect(onAdd).toHaveBeenCalled();
  });
});
