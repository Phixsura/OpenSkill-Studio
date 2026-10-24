import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ErrorPage } from "@/components/error-page";

describe("ErrorPage", () => {
  it("renders 404", () => {
    const onAction = vi.fn();
    const { container, getByText } = render(
      <ErrorPage status={404} title="Not Found" description="Resource not found"
        detail="Page /xyz" requestId="req_abc"
        actions={[{ label: "Go Home", action: "home" }]} onAction={onAction} />
    );
    expect(container.textContent).toContain("404");
    expect(container.textContent).toContain("Not Found");
    expect(container.textContent).toContain("Page /xyz");
    expect(container.textContent).toContain("req_abc");
    fireEvent.click(getByText("Go Home"));
    expect(onAction).toHaveBeenCalledWith("home");
  });
});
