import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIErrorMappingCard from "../src/components/api-error-mapping-card";

const mappings = [
  { internal_code: "DB_TIMEOUT", public_code: "SERVICE_UNAVAILABLE", http_status: 503, occurrences: 15 },
  { internal_code: "INVALID_INPUT", public_code: "BAD_REQUEST", http_status: 400, occurrences: 0 },
];

describe("APIErrorMappingCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIErrorMappingCard mappings={mappings} appName="App" />);
    expect(container.textContent).toContain("Error Mapping");
    expect(container.textContent).toContain("2 mappings");
  });

  it("shows mappings with arrow", () => {
    const { container } = render(<APIErrorMappingCard mappings={mappings} appName="App" />);
    expect(container.textContent).toContain("DB_TIMEOUT");
    expect(container.textContent).toContain("SERVICE_UNAVAILABLE");
    expect(container.textContent).toContain("503");
    expect(container.textContent).toContain("15x");
  });

  it("shows empty state", () => {
    const { container } = render(<APIErrorMappingCard mappings={[]} appName="App" />);
    expect(container.textContent).toContain("No error mappings");
  });
});
