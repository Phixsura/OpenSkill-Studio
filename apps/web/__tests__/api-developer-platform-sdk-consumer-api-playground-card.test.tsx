import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import PlaygroundCard from "../src/components/api-developer-platform-sdk-consumer-api-playground-card";

describe("PlaygroundCard", () => {
  it("renders title and requests", () => {
    const { container } = render(<PlaygroundCard />);
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("/api/orders");
  });

  it("shows methods and count", () => {
    const { container } = render(<PlaygroundCard />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("POST");
    expect(container.textContent).toContain("3 recent requests");
  });
});
