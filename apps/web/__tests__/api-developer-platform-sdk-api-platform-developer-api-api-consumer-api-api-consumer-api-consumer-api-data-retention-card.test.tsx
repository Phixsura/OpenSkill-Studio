import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-data-retention-card";

describe("ConsumerApiDataRetentionCard", () => {
  it("shows policies", () => {
    const policies = [{ dataType: "logs", retentionDays: 30, archiveFirst: true, autoDelete: true, expired: false }];
    const { container } = render(<Card policies={policies} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Data Retention");
    expect(container.textContent).toContain("logs");
    expect(container.textContent).toContain("30d");
    expect(container.textContent).toContain("archive");
    expect(container.textContent).toContain("OK");
  });
  it("shows empty", () => {
    const { container } = render(<Card policies={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No retention policies");
  });
});
