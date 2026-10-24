import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CtaBanner } from "@/components/cta-banner";

describe("CtaBanner", () => {
  it("renders CTA", () => {
    const onAction = vi.fn();
    const { container, getByText } = render(
      <CtaBanner title="Start Building" subtitle="Create your first app"
        button="Get Started" icon="🚀" variant="primary" onAction={onAction} />
    );
    expect(container.textContent).toContain("Start Building");
    expect(container.textContent).toContain("Create your first app");
    fireEvent.click(getByText("Get Started"));
    expect(onAction).toHaveBeenCalled();
  });
});
