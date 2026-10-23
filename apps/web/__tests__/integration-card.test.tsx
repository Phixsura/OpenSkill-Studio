import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { IntegrationCard } from "@/components/integration-card";

describe("IntegrationCard", () => {
  it("renders connected", () => {
    const { container } = render(
      <IntegrationCard id="github" label="GitHub" icon="🐙" category="SCM"
        connected={true} cta="Disconnect" onAction={vi.fn()} />
    );
    expect(container.textContent).toContain("GitHub");
    expect(container.textContent).toContain("SCM");
    expect(container.textContent).toContain("Disconnect");
  });
  it("renders disconnected", () => {
    const fn = vi.fn();
    const { container } = render(
      <IntegrationCard id="slack" label="Slack" icon="💬" category="Communication"
        connected={false} cta="Connect" onAction={fn} />
    );
    expect(container.textContent).toContain("Connect");
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
