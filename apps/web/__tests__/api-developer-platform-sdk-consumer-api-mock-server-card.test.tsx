import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MockServerCard from "../src/components/api-developer-platform-sdk-consumer-api-mock-server-card";

describe("MockServerCard", () => {
  it("renders title and endpoints", () => {
    const { container } = render(<MockServerCard />);
    expect(container.textContent).toContain("Mock Server");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("/api/orders");
  });

  it("shows methods and active count", () => {
    const { container } = render(<MockServerCard />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("2/3 endpoints active");
  });
});
