import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiPlaygroundExplorer } from "@/components/api-playground-explorer";

const endpoints = [
  { path: "/api/users", method: "GET", description: "List users", params: [] },
  { path: "/api/users", method: "POST", description: "Create user", params: [{ name: "name", type: "string", required: true }] },
];

describe("ApiPlaygroundExplorer", () => {
  it("renders endpoints", () => {
    const { container } = render(<ApiPlaygroundExplorer endpoints={endpoints} />);
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("POST");
  });
  it("selects endpoint", () => {
    const { container } = render(<ApiPlaygroundExplorer endpoints={endpoints} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[0]);
    expect(container.textContent).toContain("curl");
    expect(container.textContent).toContain("python");
  });
});
