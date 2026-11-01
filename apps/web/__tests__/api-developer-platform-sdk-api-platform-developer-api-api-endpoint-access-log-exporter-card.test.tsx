import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-endpoint-access-log-exporter-card";

describe("AccessLogExporterCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card entryCount={50000} statusRanges={{ "2xx": 45000, "3xx": 100, "4xx": 4000, "5xx": 900 }} formats={["json", "csv"]} appName="App" />);
    expect(container.textContent).toContain("Log Exporter");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("45000");
    expect(container.textContent).toContain("json");
  });
  it("shows empty counts", () => {
    const { container } = render(<Card entryCount={0} statusRanges={{ "2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0 }} formats={[]} appName="App" />);
    expect(container.textContent).toContain("Log Exporter");
  });
});
