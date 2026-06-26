import "@testing-library/jest-dom";
import { afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

// ResizeObserver is needed by recharts ResponsiveContainer in jsdom.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
// @ts-expect-error attach stub
global.ResizeObserver = global.ResizeObserver || ResizeObserverStub;
