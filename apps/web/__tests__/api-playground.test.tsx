import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiPlayground } from "@/components/api-playground";

describe("ApiPlayground", () => {
  it("renders", () => {
    const { container } = render(<ApiPlayground onSend={vi.fn()} />);
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("Send");
    expect(container.querySelector("select")).toBeTruthy();
  });
  it("sends request", () => {
    const fn = vi.fn();
    const { container } = render(<ApiPlayground onSend={fn} />);
    const input = container.querySelector("input")!;
    fireEvent.change(input, { target: { value: "https://api.test.com" } });
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Send")!);
    expect(fn).toHaveBeenCalledWith("GET", "https://api.test.com");
  });
});
