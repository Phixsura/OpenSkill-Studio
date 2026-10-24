import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StructuredLogViewer } from "@/components/structured-log-viewer";

describe("StructuredLogViewer", () => {
  it("renders logs", () => {
    const { container } = render(
      <StructuredLogViewer total={100} errorPct={5} byLevel={{ INFO: 80, ERROR: 5, WARN: 15 }}
        logs={[
          { level: "ERROR", message: "Connection failed", service: "api", traceId: "t1" },
          { level: "INFO", message: "Request handled", service: "api", traceId: "t2" },
        ]} />
    );
    expect(container.textContent).toContain("Structured Logs");
    expect(container.textContent).toContain("100 logs");
    expect(container.textContent).toContain("5% errors");
    expect(container.textContent).toContain("Connection failed");
    expect(container.textContent).toContain("INFO: 80");
  });
});
