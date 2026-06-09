import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useRouter } from "expo-router";
import { BoosterValue } from "../services/api";

interface Props {
  item: BoosterValue;
  compact?: boolean;
}

function getScoreColor(score: number | null): string {
  if (score == null) return "#666";
  if (score >= 1.0) return "#4ecca3";  // green — good value
  if (score >= 0.5) return "#f0a500";  // yellow — moderate
  return "#e94560";                     // red — low value
}

function getScoreLabel(score: number | null): string {
  if (score == null) return "?";
  return `${score.toFixed(1)}x`;
}

export default function BoosterValueCard({ item, compact = false }: Props) {
  const router = useRouter();
  const scoreColor = getScoreColor(item.value_score);

  return (
    <TouchableOpacity
      style={[styles.card, compact && styles.cardCompact]}
      onPress={() => router.push(`/product/${item.product.id}`)}
      activeOpacity={0.7}
    >
      <View style={styles.left}>
        <Text style={styles.name} numberOfLines={compact ? 1 : 2}>
          {item.product.name}
        </Text>
        {!compact && (
          <Text style={styles.set}>
            {item.product.set_name} ({item.product.set_code})
          </Text>
        )}
        <View style={styles.meta}>
          <Ionicons name="layers" size={12} color="#8e8e93" />
          <Text style={styles.metaText}>{item.pack_count} Packs</Text>
          {item.lowest_price != null && (
            <>
              <Text style={styles.metaDot}> / </Text>
              <Text style={styles.metaText}>{item.lowest_price.toFixed(2)} EUR</Text>
            </>
          )}
        </View>
      </View>
      <View style={styles.right}>
        {item.price_per_pack != null && (
          <Text style={styles.pricePerPack}>
            {item.price_per_pack.toFixed(2)} EUR
          </Text>
        )}
        <Text style={styles.perPackLabel}>pro Booster</Text>
        {item.value_score != null && (
          <View style={[styles.scoreBadge, { backgroundColor: scoreColor + "22", borderColor: scoreColor }]}>
            <Text style={[styles.scoreText, { color: scoreColor }]}>
              {getScoreLabel(item.value_score)}
            </Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1a1a2e",
    borderRadius: 10,
    padding: 14,
    flexDirection: "row",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#0f3460",
  },
  cardCompact: {
    width: 260,
    marginRight: 10,
  },
  left: {
    flex: 1,
    marginRight: 12,
  },
  name: {
    color: "#e0e0e0",
    fontSize: 14,
    fontWeight: "600",
  },
  set: {
    color: "#8e8e93",
    fontSize: 12,
    marginTop: 2,
  },
  meta: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 4,
    gap: 4,
  },
  metaText: {
    color: "#8e8e93",
    fontSize: 12,
  },
  metaDot: {
    color: "#8e8e93",
    fontSize: 12,
  },
  right: {
    alignItems: "flex-end",
  },
  pricePerPack: {
    color: "#4ecca3",
    fontSize: 16,
    fontWeight: "700",
  },
  perPackLabel: {
    color: "#8e8e93",
    fontSize: 10,
    marginTop: 1,
  },
  scoreBadge: {
    borderRadius: 6,
    borderWidth: 1,
    paddingHorizontal: 8,
    paddingVertical: 2,
    marginTop: 4,
  },
  scoreText: {
    fontSize: 12,
    fontWeight: "700",
  },
});
