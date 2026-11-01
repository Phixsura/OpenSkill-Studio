import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookHeaderCard from "../src/components/api-webhook-header-card";

const headers = [
  { name: "X-Custom", value: "public", secret: false },
  { name: "Authorization", value: "Be**********23", secret: true },
];

describe("APIWebhookHeaderCard", () => {
  it("renders header and count", () => {
    const { container } = render(<APIWebhookHeaderCard destination="https://hooks.example.com" headers={headers} appName="App" />);
    expect(container.textContent).toContain("Webhook Headers");
    expect(container.textContent).toContain("2 headers");
  });

  it("shows header names and values", () => {
    const { container } = render(<APIWebhookHeaderCard destination="https://a.com" headers={headers} appName="App" />);
    expect(container.textContent).toContain("X-Custom");
    expect(container.textContent).toContain("public");
    expect(container.textContent).toContain("Authorization");
  });

  it("shows empty state", () => {
    const { container } = render(<APIWebhookHeaderCard destination="" headers={[]} appName="App" />);
    expect(container.textContent).toContain("No custom headers");
  });
});
