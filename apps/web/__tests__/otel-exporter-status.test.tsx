import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OtelExporterStatus } from "@/components/otel-exporter-status";

describe("OtelExporterStatus", () => {
  it("renders status", () => {
    const onFlush = vi.fn();
    const { container, getByText } = render(
      <OtelExporterStatus buffered={45} exported={5000} batchesSent={50}
        batchSize={100} onFlush={onFlush} />
    );
    expect(container.textContent).toContain("Trace Exporter");
    expect(container.textContent).toContain("45");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("45%");
    fireEvent.click(getByText("Flush"));
    expect(onFlush).toHaveBeenCalled();
  });
});
