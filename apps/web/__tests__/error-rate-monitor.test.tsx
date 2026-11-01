import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ErrorRateMonitor } from "@/components/error-rate-monitor";

describe("ErrorRateMonitor", () => {
  it("renders", () => {
    const { container } = render(
      <ErrorRateMonitor alerting={1} allOk={false} results={[
        { service: "api", rate: 0.05, threshold: 1, breaching: false },
        { service: "worker", rate: 5, threshold: 1, breaching: true },
      ]} />
    );
    expect(container.textContent).toContain("Error Rates");
    expect(container.textContent).toContain("1 alerting");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("worker");
    expect(container.textContent).toContain("5%");
  });
});
