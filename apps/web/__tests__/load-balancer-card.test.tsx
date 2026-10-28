import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LoadBalancerCard from "../src/components/load-balancer-card";

const instances = [
  { instance_id: "i1", address: "10.0.0.1:8080", weight: 2, healthy: true, request_count: 150 },
  { instance_id: "i2", address: "10.0.0.2:8080", weight: 1, healthy: true, request_count: 75 },
  { instance_id: "i3", address: "10.0.0.3:8080", weight: 1, healthy: false, request_count: 10 },
];

describe("LoadBalancerCard", () => {
  it("renders header and summary", () => {
    const { container } = render(<LoadBalancerCard instances={instances} appName="App" />);
    expect(container.textContent).toContain("Load Balancer");
    expect(container.textContent).toContain("2/3 healthy");
    expect(container.textContent).toContain("235 reqs");
  });

  it("shows addresses", () => {
    const { container } = render(<LoadBalancerCard instances={instances} appName="App" />);
    expect(container.textContent).toContain("10.0.0.1:8080");
    expect(container.textContent).toContain("10.0.0.2:8080");
  });

  it("shows weight for weighted instances", () => {
    const { container } = render(<LoadBalancerCard instances={instances} appName="App" />);
    expect(container.textContent).toContain("w2");
  });

  it("shows request counts", () => {
    const { container } = render(<LoadBalancerCard instances={instances} appName="App" />);
    expect(container.textContent).toContain("150 reqs");
    expect(container.textContent).toContain("75 reqs");
  });

  it("shows empty state", () => {
    const { container } = render(<LoadBalancerCard instances={[]} appName="App" />);
    expect(container.textContent).toContain("No backend instances");
  });
});
