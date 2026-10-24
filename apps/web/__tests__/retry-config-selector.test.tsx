import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RetryConfigSelector } from "@/components/retry-config-selector";

describe("RetryConfigSelector", () => {
  it("renders policies", () => {
    const onSelect = vi.fn();
    const { container, getByText } = render(
      <RetryConfigSelector selected="standard" onSelect={onSelect} policies={[
        { name: "aggressive", maxRetries: 10, strategy: "exponential" },
        { name: "standard", maxRetries: 5, strategy: "exponential" },
        { name: "none", maxRetries: 0, strategy: "none" },
      ]} />
    );
    expect(container.textContent).toContain("Retry Policy");
    expect(container.textContent).toContain("aggressive");
    expect(container.textContent).toContain("10 retries");
    fireEvent.click(getByText("aggressive"));
    expect(onSelect).toHaveBeenCalledWith("aggressive");
  });
});
