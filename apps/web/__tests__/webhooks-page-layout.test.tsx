import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhooksPageLayout } from "@/components/webhooks-page-layout";

describe("WebhooksPageLayout", () => {
  it("renders", () => {
    const overview = { total_endpoints: 3, active: 2, delivery_rate: 99.5, total_deliveries: 5000 };
    const { container } = render(
      <WebhooksPageLayout appName="MyApp" overview={overview} onAddEndpoint={vi.fn()}>
        <p>Webhook content</p>
      </WebhooksPageLayout>
    );
    expect(container.textContent).toContain("MyApp Webhooks");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("Webhook content");
  });
  it("add endpoint", () => {
    const fn = vi.fn();
    const overview = { total_endpoints: 0, active: 0, delivery_rate: 0, total_deliveries: 0 };
    const { container } = render(
      <WebhooksPageLayout appName="X" overview={overview} onAddEndpoint={fn}><p>C</p></WebhooksPageLayout>
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Add"))!);
    expect(fn).toHaveBeenCalled();
  });
});
