import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ObservHubDash } from "@/components/observ-hub-dash";

describe("ObservHubDash", () => {
  it("renders", () => {
    const { container } = render(
      <ObservHubDash totalMetrics={5000} uniqueMetrics={20} totalLogs={10000}
        logLevels={{ info: 9500, error: 500 }} totalTraces={3000}
        avgTraceMs={150} activeAlerts={2}
        recentAlerts={[
          { type: "log_alert", source: "worker", message: "Process crashed" },
        ]} />
    );
    expect(container.textContent).toContain("Observability Hub");
    expect(container.textContent).toContain("2 alerts");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("20 unique");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("500 errors");
    expect(container.textContent).toContain("3,000");
    expect(container.textContent).toContain("150ms avg");
    expect(container.textContent).toContain("Process crashed");
  });
});
