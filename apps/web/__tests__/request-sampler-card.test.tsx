import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RequestSamplerCard from "../src/components/request-sampler-card";

const samples = [
  {
    sample_id: "s1",
    method: "GET",
    path: "/api/users",
    status_code: 200,
    duration_ms: 45,
    timestamp: new Date(Date.now() - 60000).toISOString(),
  },
  {
    sample_id: "s2",
    method: "POST",
    path: "/api/orders",
    status_code: 500,
    duration_ms: 120,
    timestamp: new Date(Date.now() - 300000).toISOString(),
  },
];

describe("RequestSamplerCard", () => {
  it("renders header", () => {
    const { container } = render(
      <RequestSamplerCard samples={samples} sampleRate={0.1} totalSamples={50} appName="My App" />,
    );
    expect(container.textContent).toContain("Request Sampler");
  });

  it("shows sample rate and count", () => {
    const { container } = render(
      <RequestSamplerCard samples={samples} sampleRate={0.1} totalSamples={50} appName="App" />,
    );
    expect(container.textContent).toContain("10% rate");
    expect(container.textContent).toContain("50 stored");
  });

  it("renders methods and paths", () => {
    const { container } = render(
      <RequestSamplerCard samples={samples} sampleRate={0.1} totalSamples={50} appName="App" />,
    );
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
  });

  it("shows status and duration", () => {
    const { container } = render(
      <RequestSamplerCard samples={samples} sampleRate={0.1} totalSamples={50} appName="App" />,
    );
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("45ms");
  });

  it("shows empty state", () => {
    const { container } = render(
      <RequestSamplerCard samples={[]} sampleRate={0.1} totalSamples={0} appName="App" />,
    );
    expect(container.textContent).toContain("No samples captured");
  });
});
