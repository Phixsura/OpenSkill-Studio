import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LoadBalancerCard from "../src/components/api-developer-platform-sdk-consumer-api-load-balancer-card";

describe("LoadBalancerCard", () => {
  it("renders title and targets", () => {
    const { container } = render(<LoadBalancerCard />);
    expect(container.textContent).toContain("Load Balancer");
    expect(container.textContent).toContain("us-east-1:8080");
    expect(container.textContent).toContain("eu-west-1:8080");
  });

  it("shows health and connections", () => {
    const { container } = render(<LoadBalancerCard />);
    expect(container.textContent).toContain("42 conn");
    expect(container.textContent).toContain("2/3 targets healthy");
  });
});
