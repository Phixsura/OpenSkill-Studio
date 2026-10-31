import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIMockCard from "../src/components/api-mock-card";

const mocks = [
  {
    mock_id: "m1",
    method: "GET",
    path: "/api/users",
    status_code: 200,
    hit_count: 42,
    delay_ms: 0,
  },
  {
    mock_id: "m2",
    method: "POST",
    path: "/api/orders",
    status_code: 201,
    hit_count: 15,
    delay_ms: 100,
  },
];

describe("APIMockCard", () => {
  it("renders header", () => {
    const { container } = render(<APIMockCard mocks={mocks} appName="My App" />);
    expect(container.textContent).toContain("API Mocks");
  });

  it("shows mock and hit counts", () => {
    const { container } = render(<APIMockCard mocks={mocks} appName="App" />);
    expect(container.textContent).toContain("2 mocks");
    expect(container.textContent).toContain("57 hits");
  });

  it("renders methods and paths", () => {
    const { container } = render(<APIMockCard mocks={mocks} appName="App" />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("→ 200");
  });

  it("shows hit count per mock", () => {
    const { container } = render(<APIMockCard mocks={mocks} appName="App" />);
    expect(container.textContent).toContain("42 hits");
  });

  it("shows empty state", () => {
    const { container } = render(<APIMockCard mocks={[]} appName="App" />);
    expect(container.textContent).toContain("No mocks defined");
  });
});
