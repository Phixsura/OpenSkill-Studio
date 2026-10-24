import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DiContainerViewer } from "@/components/di-container-viewer";

describe("DiContainerViewer", () => {
  it("renders", () => {
    const { container } = render(
      <DiContainerViewer registered={3} singletonsCreated={1}
        services={[
          { name: "database", singleton: true, instantiated: true },
          { name: "logger", singleton: true, instantiated: false },
          { name: "handler", singleton: false, instantiated: false },
        ]} />
    );
    expect(container.textContent).toContain("DI Container");
    expect(container.textContent).toContain("3 registered");
    expect(container.textContent).toContain("1 singletons");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("singleton");
    expect(container.textContent).toContain("transient");
  });
});
