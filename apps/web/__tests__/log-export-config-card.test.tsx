import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LogExportConfigCard } from "@/components/log-export-config-card";

describe("LogExportConfigCard", () => {
  it("renders config", () => {
    const { container } = render(
      <LogExportConfigCard destination="datadog" endpointUrl="https://intake.datadoghq.com"
        status="configured" format="json" filters={["*"]} onTest={vi.fn()} onDisable={vi.fn()} />
    );
    expect(container.textContent).toContain("datadog");
    expect(container.textContent).toContain("configured");
    expect(container.textContent).toContain("json");
  });
  it("test button", () => {
    const fn = vi.fn();
    const { container } = render(
      <LogExportConfigCard destination="splunk" endpointUrl="x" status="configured"
        format="hec" filters={[]} onTest={fn} onDisable={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Test")!);
    expect(fn).toHaveBeenCalled();
  });
});
