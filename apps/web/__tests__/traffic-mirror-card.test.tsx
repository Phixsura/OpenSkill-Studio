import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TrafficMirrorCard from "../src/components/traffic-mirror-card";

const rules = [
  {
    rule_id: "r1",
    source_path: "/api/users",
    shadow_target: "https://shadow.example.com/api/users",
    sample_rate: 1.0,
    enabled: true,
    mirrored_count: 1500,
    divergence_rate: 2.5,
  },
  {
    rule_id: "r2",
    source_path: "/api/orders",
    shadow_target: "https://shadow.example.com/api/orders",
    sample_rate: 0.1,
    enabled: false,
    mirrored_count: 50,
    divergence_rate: 8.0,
  },
];

describe("TrafficMirrorCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<TrafficMirrorCard rules={rules} appName="My App" />);
    expect(container.textContent).toContain("Traffic Mirror");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(<TrafficMirrorCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("1/2 active");
  });

  it("renders source and target", () => {
    const { container } = render(<TrafficMirrorCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("→");
  });

  it("shows sample rate", () => {
    const { container } = render(<TrafficMirrorCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("10%");
  });

  it("shows mirrored count", () => {
    const { container } = render(<TrafficMirrorCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("1.5K mirrored");
  });

  it("shows divergence rate", () => {
    const { container } = render(<TrafficMirrorCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("2.5% divergence");
  });

  it("shows empty state", () => {
    const { container } = render(<TrafficMirrorCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No mirror rules");
  });
});
