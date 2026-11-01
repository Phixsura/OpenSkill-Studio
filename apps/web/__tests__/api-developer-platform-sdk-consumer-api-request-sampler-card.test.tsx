import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RequestSamplerCard from "../src/components/api-developer-platform-sdk-consumer-api-request-sampler-card";

describe("RequestSamplerCard", () => {
  it("renders title and rules", () => {
    const { container } = render(<RequestSamplerCard />);
    expect(container.textContent).toContain("Request Sampler");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("/api/orders");
  });

  it("shows stats", () => {
    const { container } = render(<RequestSamplerCard />);
    expect(container.textContent).toContain("8,450 sampled");
    expect(container.textContent).toContain("6.76%");
  });
});
