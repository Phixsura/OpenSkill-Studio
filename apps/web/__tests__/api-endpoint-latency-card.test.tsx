import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIEndpointLatencyCard from "../src/components/api-endpoint-latency-card";

const eps = [{ method: "GET", path: "/api/users", avg: 45.2, p99: 350 }];

describe("APIEndpointLatencyCard", () => {
  it("shows latency", () => {
    const { container } = render(<APIEndpointLatencyCard endpoints={eps} appName="App" />);
    expect(container.textContent).toContain("45.2ms avg");
    expect(container.textContent).toContain("350ms p99");
  });
  it("shows empty", () => {
    const { container } = render(<APIEndpointLatencyCard endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No latency data");
  });
});
