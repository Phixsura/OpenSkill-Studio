import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WebhookEndpointList } from "@/components/webhook-endpoint-list";

describe("WebhookEndpointList", () => {
  const endpoints = [
    { id: "we1", url: "https://example.com/hook", events: ["app.installed"], active: true, description: "Main" },
  ];
  it("renders endpoints", () => {
    const { container } = render(
      <WebhookEndpointList endpoints={endpoints} active={1} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    expect(container.textContent).toContain("https://example.com/hook");
    expect(container.textContent).toContain("app.installed");
    expect(container.textContent).toContain("1 active");
  });
});
