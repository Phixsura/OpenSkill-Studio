import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DataRetentionCard from "../src/components/api-developer-platform-sdk-consumer-api-data-retention-card";

describe("DataRetentionCard", () => {
  it("renders title and categories", () => {
    const { container } = render(<DataRetentionCard />);
    expect(container.textContent).toContain("Data Retention");
    expect(container.textContent).toContain("Logs");
    expect(container.textContent).toContain("Audit");
  });

  it("shows retention days and policy count", () => {
    const { container } = render(<DataRetentionCard />);
    expect(container.textContent).toContain("30d");
    expect(container.textContent).toContain("365d");
    expect(container.textContent).toContain("4 policies configured");
  });
});
