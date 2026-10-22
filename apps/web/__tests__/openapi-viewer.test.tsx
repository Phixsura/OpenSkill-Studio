import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OpenApiViewer } from "@/components/openapi-viewer";

describe("OpenApiViewer", () => {
  it("renders API spec", () => {
    const endpoints = [
      { path: "/users", method: "GET", summary: "List users" },
      { path: "/users", method: "POST", summary: "Create user" },
    ];
    const { container } = render(
      <OpenApiViewer title="MyApp API" version="2.0.0" endpoints={endpoints} serverUrl="https://api.example.com" />
    );
    expect(container.textContent).toContain("MyApp API");
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("List users");
  });
});
