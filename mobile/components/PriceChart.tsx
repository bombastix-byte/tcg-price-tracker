import { View, Text, Dimensions, StyleSheet } from "react-native";
import { LineChart } from "react-native-chart-kit";
import { PriceHistoryPoint } from "../services/api";

const screenWidth = Dimensions.get("window").width - 48;

const COLORS: Record<string, string> = {
  cardmarket: "#0070ba",
  ebay: "#e53238",
  amazon: "#ff9900",
};

interface Props {
  data: PriceHistoryPoint[];
}

export default function PriceChart({ data }: Props) {
  if (data.length < 2) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>Not enough data for chart</Text>
      </View>
    );
  }

  const labels = data.map((d) => {
    const parts = d.date.split("-");
    return `${parts[2]}/${parts[1]}`;
  });

  // Show at most 6 labels to avoid crowding
  const step = Math.max(1, Math.floor(labels.length / 6));
  const displayLabels = labels.map((l, i) => (i % step === 0 ? l : ""));

  const datasets: { data: number[]; color: () => string; strokeWidth: number }[] = [];
  const legend: string[] = [];

  for (const mp of ["cardmarket", "ebay", "amazon"] as const) {
    const values = data.map((d) => d[mp]);
    if (values.every((v) => v === null)) continue;

    // Fill nulls with previous value for continuity
    const filled: number[] = [];
    let last = 0;
    for (const v of values) {
      if (v !== null) last = v;
      filled.push(last);
    }

    const color = COLORS[mp] || "#666";
    datasets.push({
      data: filled,
      color: () => color,
      strokeWidth: 2,
    });
    legend.push(mp.charAt(0).toUpperCase() + mp.slice(1));
  }

  if (datasets.length === 0) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>No price history available</Text>
      </View>
    );
  }

  return (
    <View>
      <LineChart
        data={{ labels: displayLabels, datasets, legend }}
        width={screenWidth}
        height={220}
        yAxisSuffix=" EUR"
        chartConfig={{
          backgroundColor: "#1a1a2e",
          backgroundGradientFrom: "#1a1a2e",
          backgroundGradientTo: "#16213e",
          decimalPlaces: 0,
          color: (opacity = 1) => `rgba(224, 224, 224, ${opacity})`,
          labelColor: (opacity = 1) => `rgba(142, 142, 147, ${opacity})`,
          propsForDots: { r: "3" },
          propsForBackgroundLines: {
            stroke: "#0f3460",
            strokeDasharray: "",
          },
        }}
        bezier
        style={styles.chart}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  chart: { borderRadius: 12 },
  empty: {
    backgroundColor: "#1a1a2e",
    borderRadius: 12,
    padding: 30,
    alignItems: "center",
  },
  emptyText: { color: "#666", fontSize: 14 },
});
