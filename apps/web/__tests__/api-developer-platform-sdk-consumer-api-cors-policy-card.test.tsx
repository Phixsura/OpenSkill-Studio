import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CorsPolicyCard from "../src/components/api-developer-platform-sdk-consumer-api-cors-policy-card";

describe("CorsPolicyCard", () => {
  it("renders title and origins", () => {
    const { container } = render(<CorsPolicyCard />);
    expect(container.textContent).toContain("CORS Policy");
    expect(container.textContent).toContain("https://app.acme.com");
    expect(container.textContent).toContain("localhost:3000");
  });

  it("shows methods and credentials", () => {
    const { container } = render(<CorsPolicyCard />);
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("DELETE");
    expect(container.textContent).toContain("enabled");
    expect(container.textContent).toContain("3 origins");
  });
});
