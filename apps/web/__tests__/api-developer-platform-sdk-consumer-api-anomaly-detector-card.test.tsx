import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AnomalyDetectorCard from "../src/components/api-developer-platform-sdk-consumer-api-anomaly-detector-card";

describe("AnomalyDetectorCard", () => {
  it("renders title and anomalies", () => {
    const { container } = render(<AnomalyDetectorCard />);
    expect(container.textContent).toContain("Anomaly Detector");
    expect(container.textContent).toContain("latency_p99");
    expect(container.textContent).toContain("error_rate");
  });

  it("shows severity and count", () => {
    const { container } = render(<AnomalyDetectorCard />);
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("3 anomalies detected");
  });
});
