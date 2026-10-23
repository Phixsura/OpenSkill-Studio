import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TelemetryPipelineEditor } from "@/components/telemetry-pipeline-editor";

describe("TelemetryPipelineEditor", () => {
  const pipelines = [
    { pipeline_id: "p1", name: "Main", sources: ["otlp"], destinations: ["datadog"], status: "active" },
  ];
  it("renders", () => {
    const { container } = render(
      <TelemetryPipelineEditor pipelines={pipelines} onToggle={vi.fn()} onDelete={vi.fn()} onCreate={vi.fn()} />
    );
    expect(container.textContent).toContain("Telemetry Pipelines");
    expect(container.textContent).toContain("Main");
    expect(container.textContent).toContain("otlp");
    expect(container.textContent).toContain("datadog");
  });
  it("delete", () => {
    const fn = vi.fn();
    const { container } = render(
      <TelemetryPipelineEditor pipelines={pipelines} onToggle={vi.fn()} onDelete={fn} onCreate={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Delete")!);
    expect(fn).toHaveBeenCalledWith("p1");
  });
});
