import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PromoBanner } from "@/components/promo-banner";

describe("PromoBanner", () => {
  it("renders banner", () => {
    const onClick = vi.fn();
    const onDismiss = vi.fn();
    const { container, getByText } = render(
      <PromoBanner title="DevCon 2026" body="Join us!" cta="Register"
        gradient="from-purple-600 to-indigo-600" icon="🎪"
        onClick={onClick} onDismiss={onDismiss} />
    );
    expect(container.textContent).toContain("DevCon 2026");
    expect(container.textContent).toContain("Join us!");
    fireEvent.click(getByText("Register"));
    expect(onClick).toHaveBeenCalled();
    fireEvent.click(getByText("✕"));
    expect(onDismiss).toHaveBeenCalled();
  });
});
