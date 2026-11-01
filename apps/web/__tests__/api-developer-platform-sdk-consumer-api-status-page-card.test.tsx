import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import StatusPageCard from "../src/components/api-developer-platform-sdk-consumer-api-status-page-card";

describe("StatusPageCard", () => {
  it("renders title and components", () => {
    const { container } = render(<StatusPageCard />);
    expect(container.textContent).toContain("Status Page");
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("Database");
  });

  it("shows operational count", () => {
    const { container } = render(<StatusPageCard />);
    expect(container.textContent).toContain("4/5 operational");
  });
});
