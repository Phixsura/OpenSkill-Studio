import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LoadBalancerCard from "../src/components/load-balancer-card";

const instances = [
  { instance_id: "i1", address: "10.0.0.1:8080", weight: 3, healthy: true, request_count: 1500 },
  { instance_id: "i2", address: "10.0.0.2:8080", weight: 1, healthy: true, request_count: 500 },
  { instance_id: "i3", address: "10.0.0.3:8080", weight: 1, healthy: false, request_count: 200 },
];

describe("LoadBalancerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<LoadBalancerCard instances={instances} appName="My App" />);
    expect(container.textContent).toContain("Load Balancer");
    expect(container.textContent).toContain("My App");
  });

  it("shows healthy count", () => {
    const { container } = render(<LoadBalancerCard instances={instances} appName="App" />);
    expect(container.textContent).toContain("2/3 healthy");
  });

  it("shows total requests", () => {
    const { container } = render(<LoadBalancerCard instances={instances} appName="App" />);
    expect(container.textContent).toContain("2.2K req");
  });

  it("renders addresses", () => {
    const { container } = render(<LoadBalancerCard instances={instances} appName="App" />);
    expect(container.textContent).toContain("10.0.0.1:8080");
    expect(container.textContent).toContain("10.0.0.2:8080");
  });

  it("shows weight for heavy instances", () => {
    const { container } = render(<LoadBalancerCard instances={instances} appName="App" />);
    expect(container.textContent).toContain("w3");
  });

  it("shows per-instance request count", () => {
    const { container } = render(<LoadBalancerCard instances={instances} appName="App" />);
    expect(container.textContent).toContain("1.5K req");
  });

  it("shows empty state", () => {
    const { container } = render(<LoadBalancerCard instances={[]} appName="App" />);
    expect(container.textContent).toContain("No instances");
  });
});
