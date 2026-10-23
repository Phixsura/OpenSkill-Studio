import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StructuredLogViewer } from "@/components/structured-log-viewer";

describe("StructuredLogViewer", () => {
  it("renders logs", () => {
    const { container } = render(
      <StructuredLogViewer total={3} hasErrors={true}
        byLevel={{ info: 2, error: 1 }}
        logs={[
          { level: "info", service: "api", message: "Request handled" },
          { level: "error", service: "api", message: "DB timeout" },
        ]} />
    );
    expect(container.textContent).toContain("Logs");
    expect(container.textContent).toContain("info: 2");
    expect(container.textContent).toContain("error: 1");
    expect(container.textContent).toContain("DB timeout");
    expect(container.textContent).toContain("3 total entries");
  });
});
