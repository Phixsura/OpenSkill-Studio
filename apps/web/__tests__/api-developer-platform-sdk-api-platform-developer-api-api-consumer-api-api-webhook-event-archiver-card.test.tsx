import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-event-archiver-card";

describe("WebhookEventArchiverCard", () => {
  it("shows archive stats", () => {
    const { container } = render(<Card totalArchived={50000} totalSizeKb={25600} retentionDays={90} appName="App" />);
    expect(container.textContent).toContain("Event Archiver");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("25,600 KB");
    expect(container.textContent).toContain("90d retention");
  });
  it("shows zero", () => {
    const { container } = render(<Card totalArchived={0} totalSizeKb={0} retentionDays={30} appName="App" />);
    expect(container.textContent).toContain("30d retention");
  });
});
