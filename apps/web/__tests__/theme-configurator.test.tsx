import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ThemeConfigurator } from "@/components/theme-configurator";

describe("ThemeConfigurator", () => {
  const colors = { primary: "#3B82F6", secondary: "#6366F1" };
  it("renders color inputs and font select", () => {
    const { container } = render(
      <ThemeConfigurator colors={colors} font="Inter" borderRadius={8} availableFonts={["Inter", "Roboto"]} onChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Theme");
    expect(container.textContent).toContain("primary");
    expect(container.querySelector("select")).toBeTruthy();
    expect(container.querySelector("input[type='range']")).toBeTruthy();
  });
});
