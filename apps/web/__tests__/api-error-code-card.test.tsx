import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIErrorCodeCard from "../src/components/api-error-code-card";

const codes = [
  { code: "AUTH_EXPIRED", message: "Token expired", http_status: 401, category: "auth", retryable: false },
  { code: "RATE_LIMIT", message: "Too many requests", http_status: 429, category: "rate", retryable: true },
  { code: "INTERNAL", message: "Server error", http_status: 500, category: "server", retryable: true },
];

describe("APIErrorCodeCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIErrorCodeCard codes={codes} appName="App" />);
    expect(container.textContent).toContain("Error Codes");
    expect(container.textContent).toContain("3 codes");
  });

  it("shows codes and status", () => {
    const { container } = render(<APIErrorCodeCard codes={codes} appName="App" />);
    expect(container.textContent).toContain("AUTH_EXPIRED");
    expect(container.textContent).toContain("401");
    expect(container.textContent).toContain("500");
  });

  it("shows retryable and category", () => {
    const { container } = render(<APIErrorCodeCard codes={codes} appName="App" />);
    expect(container.textContent).toContain("retryable");
    expect(container.textContent).toContain("auth");
  });

  it("shows empty state", () => {
    const { container } = render(<APIErrorCodeCard codes={[]} appName="App" />);
    expect(container.textContent).toContain("No error codes defined");
  });
});
