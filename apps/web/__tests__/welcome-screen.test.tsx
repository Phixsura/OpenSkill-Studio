import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WelcomeScreen } from "@/components/welcome-screen";

describe("WelcomeScreen", () => {
  it("renders new user", () => {
    const onCta = vi.fn();
    const { container, getByText } = render(
      <WelcomeScreen greeting="Welcome, Alice! 👋" message="Let's get started"
        type="new_user" steps={["Create app", "Gen key"]} ctaLabel="Get Started" onCta={onCta} />
    );
    expect(container.textContent).toContain("Welcome, Alice!");
    expect(container.textContent).toContain("Create app");
    expect(container.textContent).toContain("Gen key");
    fireEvent.click(getByText("Get Started"));
    expect(onCta).toHaveBeenCalled();
  });
});
