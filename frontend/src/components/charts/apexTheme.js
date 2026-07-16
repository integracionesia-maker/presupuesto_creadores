/**
 * Shared ApexCharts theme configuration — Grupo Ortiz design system.
 * Every chart component imports this to stay visually consistent.
 */

export const GO_CHART_COLORS = [
  "#FB670B", // go-orange
  "#14B8A6", // turquoise
  "#38BDF8", // sky
  "#A78BFA", // violet
  "#00A36E", // go-success
  "#F59E0B", // go-warning
];

const GO_DARK_700 = "#18181b";
const GO_DARK_600 = "#27272a";
const GO_GRAY_2 = "#c5c5c5";
const GO_WHITE = "#ffffff";

export const goApexTheme = {
  mode: "dark",
  palette: "palette1",
  monochrome: { enabled: false },
};

export const goApexGrid = {
  borderColor: GO_DARK_600,
  strokeDashArray: 3,
  xaxis: { lines: { show: false } },
  yaxis: { lines: { show: true } },
};

/**
 * Returns a base ApexCharts options object pre-filled with GO theme values.
 * Pass per-chart overrides via the `overrides` parameter.
 */
export function createApexOptions(overrides = {}) {
  const options = {
    chart: {
      background: "transparent",
      fontFamily: "'Inter', sans-serif",
      foreColor: GO_GRAY_2,
      toolbar: { show: false },
      zoom: { enabled: false },
      ...overrides.chart,
    },
    theme: { ...goApexTheme, ...overrides.theme },
    colors: overrides.colors || GO_CHART_COLORS,
    grid: { ...goApexGrid, ...overrides.grid },
    tooltip: {
      theme: "dark",
      style: { fontSize: "12px", fontFamily: "'Inter', sans-serif" },
      ...overrides.tooltip,
    },
    legend: {
      fontSize: "12px",
      fontFamily: "'Inter', sans-serif",
      labels: { colors: GO_GRAY_2 },
      markers: { width: 10, height: 10, radius: 3 },
      ...overrides.legend,
    },
    dataLabels: {
      style: { colors: [GO_WHITE], fontSize: "11px", fontFamily: "'Inter', sans-serif" },
      ...overrides.dataLabels,
    },
    xaxis: {
      labels: { style: { fontSize: "11px", fontFamily: "'Inter', sans-serif", colors: GO_GRAY_2 } },
      axisBorder: { color: GO_DARK_600 },
      axisTicks: { color: GO_DARK_600 },
      ...overrides.xaxis,
    },
    yaxis: {
      labels: { style: { fontSize: "11px", fontFamily: "'Inter', sans-serif", colors: GO_GRAY_2 } },
      ...overrides.yaxis,
    },
  };

  // Only set these when actually overridden — ApexCharts merges its own
  // defaults (e.g. plotOptions.line, responsive: []) only when the key is
  // absent; an explicit `undefined` wipes out that default and crashes.
  if (overrides.stroke) options.stroke = overrides.stroke;
  if (overrides.fill) options.fill = overrides.fill;
  if (overrides.plotOptions) options.plotOptions = overrides.plotOptions;
  if (overrides.responsive) options.responsive = overrides.responsive;

  return options;
}

/** Format a number as MXN currency — short form for chart labels */
export function formatChartCurrency(value) {
  if (value >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(1)}M`;
  }
  if (value >= 1_000) {
    return `$${(value / 1_000).toFixed(0)}k`;
  }
  return `$${value.toFixed(0)}`;
}
