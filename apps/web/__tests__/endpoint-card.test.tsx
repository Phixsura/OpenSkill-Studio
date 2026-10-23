import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EndpointCard } from "@/components/endpoint-card";

describe("EndpointCard", () => {
  it("renders", () => {
    const { container } = render(
      <EndpointCard method="GET" path="/users" summary="List users" authRequired={true}
        curlExample="curl https://api.com/users" onTry={vi.fn()} />
    );
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/users");
    expect(container.textContent).toContain("List users");
    expect(container.textContent).toContain("🔒");
  });
  it("try button", () => {
    const fn = vi.fn();
    const { container } = render(
      <EndpointCard method="POST" path="/apps" summary="Create" authRequired={false}
        curlExample="" onTry={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Try"))!);
    expect(fn).toHaveBeenCalled();
  });
});
