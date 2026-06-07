import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Product } from "../services/api";

const CATEGORY_LABELS: Record<string, string> = {
  booster_box: "Booster Box",
  etb: "ETB",
  blister: "Blister",
  booster_pack: "Booster Pack",
  collection_box: "Collection Box",
  bundle: "Bundle",
  other: "Other",
};

interface Props {
  product: Product;
}

export default function ProductCard({ product }: Props) {
  const router = useRouter();

  const lowestPrice = product.lowest_prices
    ? Math.min(
        ...Object.values(product.lowest_prices).filter(
          (v): v is number => v !== null
        )
      )
    : null;

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={() => router.push(`/product/${product.id}`)}
      activeOpacity={0.7}
    >
      <View style={styles.iconContainer}>
        <Ionicons
          name={product.tcg === "pokemon" ? "flash" : "sparkles"}
          size={28}
          color={product.tcg === "pokemon" ? "#f0a500" : "#7b68ee"}
        />
      </View>
      <View style={styles.info}>
        <Text style={styles.tcgLabel}>{product.tcg.toUpperCase()}</Text>
        <Text style={styles.name} numberOfLines={2}>
          {product.name}
        </Text>
        <Text style={styles.meta}>
          {CATEGORY_LABELS[product.category] || product.category}
          {product.set_name ? ` - ${product.set_name}` : ""}
        </Text>
      </View>
      <View style={styles.priceContainer}>
        {lowestPrice !== null && isFinite(lowestPrice) ? (
          <>
            <Text style={styles.priceLabel}>from</Text>
            <Text style={styles.price}>{lowestPrice.toFixed(2)}</Text>
            <Text style={styles.currency}>EUR</Text>
          </>
        ) : (
          <Text style={styles.noPrice}>--</Text>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1a1a2e",
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    flexDirection: "row",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#0f3460",
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 10,
    backgroundColor: "#16213e",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },
  info: { flex: 1 },
  tcgLabel: {
    color: "#e94560",
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 1,
  },
  name: {
    color: "#e0e0e0",
    fontSize: 15,
    fontWeight: "600",
    marginTop: 2,
  },
  meta: { color: "#8e8e93", fontSize: 12, marginTop: 2 },
  priceContainer: { alignItems: "flex-end", marginLeft: 8 },
  priceLabel: { color: "#8e8e93", fontSize: 10 },
  price: { color: "#4ecca3", fontSize: 18, fontWeight: "700" },
  currency: { color: "#8e8e93", fontSize: 10 },
  noPrice: { color: "#666", fontSize: 16 },
});
