import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookValidatorCard from "../src/components/api-webhook-validator-card";

describe("APIWebhookValidatorCard", () => {
  it("shows valid", () => {
    const { container } = render(<APIWebhookValidatorCard issues={[]} url="https://a.com" appName="App" />);
    expect(container.textContent).toContain("Valid");
  });
  it("shows issues", () => {
    const { container } = render(<APIWebhookValidatorCard issues={[{ field: "url", message: "Must be HTTPS" }]} url="" appName="App" />);
    expect(container.textContent).toContain("1 issues");
    expect(container.textContent).toContain("Must be HTTPS");
  });
});
