import { View, Text, StyleSheet, Linking, TouchableOpacity } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Price, MarketplaceLink } from "../services/api";

const MP_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  cardmarket: { label: "Cardmarket", color: "#0070ba", icon: "storefront" },
  ebay: { label: "eBay", color: "#e53238", icon: "pricetag" },
  amazon: { label: "Amazon", color: "#ff9900", icon: "cart" },
  idealo: { label: "Idealo", color: "#1a5ea4", icon: "search" },
  geizhals: { label: "Geizhals", color: "#ff6600", icon: "flame" },
};

interface Props {
  marketplace: string;
  price: Price | null;
  link?: MarketplaceLink | null;
}

export default function MarketplacePrice({ marketplace, price, link }: Props) {
  const config = MP_CONFIG[marketplace] || {
    label: marketplace,
    color: "#666",
    icon: "help-circle",
  };

  const openUrl = price?.url || link?.url || "";

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={() => openUrl && Linking.openURL(openUrl)}
      disabled={!openUrl}
      activeOpacity={0.7}
    >
      <View style={[styles.indicator, { backgroundColor: config.color }]} />
      <Ionicons
        name={config.icon as any}
        size={22}
        color={config.color}
        style={{ marginRight: 10 }}
      />
      <View style={{ flex: 1 }}>
        <Text style={styles.mpName}>{config.label}</Text>
        {price?.seller ? (
          <Text style={styles.seller} numberOfLines={1}>
            {price.seller}
          </Text>
        ) : null}
      </View>
      {price ? (
        <View style={styles.priceBox}>
          <Text style={styles.priceText}>
            {price.price.toFixed(2)} {price.currency}
          </Text>
        </View>
      ) : (
        <Text style={styles.noPrice}>No data</Text>
      )}
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
  indicator: {
    width: 4,
    height: 30,
    borderRadius: 2,
    marginRight: 10,
  },
  mpName: { color: "#e0e0e0", fontSize: 15, fontWeight: "600" },
  seller: { color: "#8e8e93", fontSize: 12, marginTop: 2 },
  priceBox: {
    backgroundColor: "#16213e",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  priceText: { color: "#4ecca3", fontSize: 16, fontWeight: "700" },
  noPrice: { color: "#666", fontSize: 14 },
});
