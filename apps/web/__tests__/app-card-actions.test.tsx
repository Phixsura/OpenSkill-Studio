import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppCardActions } from "@/components/app-card-actions";

describe("AppCardActions", () => {
  it("renders actions", () => {
    const onAction = vi.fn();
    const { container, getByText } = render(
      <AppCardActions onAction={onAction} actions={[
        { id: "install", label: "Install", icon: "📥", variant: "primary" },
        { id: "favorite", label: "Favorite", icon: "🤍", variant: "secondary" },
      ]} />
    );
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("Favorite");
    fireEvent.click(getByText(/Install/));
    expect(onAction).toHaveBeenCalledWith("install");
  });
});
