import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqCorrelationViewer } from "@/components/req-correlation-viewer";

describe("ReqCorrelationViewer", () => {
  it("renders traces", () => {
    const { container } = render(
      <ReqCorrelationViewer totalTraces={2} totalSpans={5} traces={[
        { correlationId: "cor_abc123", spanCount: 3, totalMs: 150, services: ["api", "db"] },
        { correlationId: "cor_def456", spanCount: 2, totalMs: 80, services: ["api"] },
      ]} />
    );
    expect(container.textContent).toContain("Request Correlation");
    expect(container.textContent).toContain("2 traces");
    expect(container.textContent).toContain("5 spans");
    expect(container.textContent).toContain("cor_abc123");
    expect(container.textContent).toContain("3 spans");
    expect(container.textContent).toContain("150ms");
  });
});
