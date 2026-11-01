import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiChangelogSubscribe } from "@/components/api-changelog-subscribe";

describe("ApiChangelogSubscribe", () => {
  it("renders form", () => {
    const onSub = vi.fn();
    const { container, getByPlaceholderText, getByText } = render(
      <ApiChangelogSubscribe versions={["v1", "v2"]} onSubscribe={onSub} />
    );
    expect(container.textContent).toContain("API Change Notifications");
    expect(container.textContent).toContain("v1, v2");
    fireEvent.change(getByPlaceholderText("your@email.com"), { target: { value: "test@test.com" } });
    fireEvent.click(getByText("Subscribe"));
    expect(onSub).toHaveBeenCalled();
  });
});
