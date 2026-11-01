import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TracingConfigPanel } from "@/components/tracing-config-panel";

describe("TracingConfigPanel", () => {
  it("renders config", () => {
    const { container } = render(
      <TracingConfigPanel serviceName="api" exporter="otlp" sampler="probability"
        sampleRate={0.1} dailySpans={43200000} storageGbDay={43.2}
        exporters={["otlp", "jaeger", "zipkin"]} onChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Tracing: api");
    expect(container.textContent).toContain("otlp");
    expect(container.textContent).toContain("10%");
    expect(container.textContent).toContain("43.2M");
    expect(container.textContent).toContain("43.2 GB");
    expect(container.textContent).toContain("jaeger");
  });
});
