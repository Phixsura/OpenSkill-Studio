import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiPlaygroundPanel } from "@/components/api-playground-panel";

describe("ApiPlaygroundPanel", () => {
  it("renders and sends", () => {
    const onSend = vi.fn();
    const { container, getByText } = render(
      <ApiPlaygroundPanel baseUrl="https://api.openskill.io" onSend={onSend}
        response={{ status: 200, body: { data: [] } }} />
    );
    expect(container.textContent).toContain("API Playground");
    expect(container.textContent).toContain("200");
    fireEvent.click(getByText("Send"));
    expect(onSend).toHaveBeenCalled();
  });
});
