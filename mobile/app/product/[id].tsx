import { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert as RNAlert,
  TextInput,
  Linking,
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import {
  getProduct,
  getPrices,
  refreshPrices,
  getPriceHistory,
  createAlert,
  Product,
  Price,
  PriceHistoryPoint,
  MarketplaceLink,
} from "../../services/api";
import { toggleWatchlist, getWatchlist } from "../(tabs)/watchlist";
import MarketplacePrice from "../../components/MarketplacePrice";
import PriceChart from "../../components/PriceChart";

const DEVICE_TOKEN = "ExponentPushToken[placeholder]";

export default function ProductDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const productId = Number(id);

  const [product, setProduct] = useState<Product | null>(null);
  const [prices, setPrices] = useState<Price[]>([]);
  const [history, setHistory] = useState<PriceHistoryPoint[]>([]);
  const [inWatchlist, setInWatchlist] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [alertPrice, setAlertPrice] = useState("");

  useEffect(() => {
    loadData();
  }, [productId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [prod, priceList, hist, wl] = await Promise.all([
        getProduct(productId),
        getPrices(productId),
        getPriceHistory(productId),
        getWatchlist(),
      ]);
      setProduct(prod);
      setPrices(priceList);
      setHistory(hist);
      setInWatchlist(wl.includes(productId));
    } catch {
      RNAlert.alert("Error", "Failed to load product");
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const newPrices = await refreshPrices(productId);
      setPrices(newPrices);
    } catch {
      RNAlert.alert("Error", "Failed to refresh prices");
    } finally {
      setRefreshing(false);
    }
  };

  const handleToggleWatchlist = async () => {
    const added = await toggleWatchlist(productId);
    setInWatchlist(added);
  };

  const handleCreateAlert = async () => {
    const price = parseFloat(alertPrice);
    if (isNaN(price) || price <= 0) {
      RNAlert.alert("Invalid price", "Please enter a valid target price.");
      return;
    }
    try {
      await createAlert({
        product_id: productId,
        user_device_token: DEVICE_TOKEN,
        target_price: price,
        direction: "below",
      });
      RNAlert.alert("Alert created", `You'll be notified when the price drops below ${price.toFixed(2)} EUR.`);
      setAlertPrice("");
    } catch {
      RNAlert.alert("Error", "Failed to create alert");
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#e94560" />
      </View>
    );
  }

  if (!product) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Product not found.</Text>
      </View>
    );
  }

  // Group latest prices by marketplace
  const latestByMarketplace: Record<string, Price> = {};
  for (const p of prices) {
    if (!latestByMarketplace[p.marketplace] ||
        new Date(p.scraped_at) > new Date(latestByMarketplace[p.marketplace].scraped_at)) {
      latestByMarketplace[p.marketplace] = p;
    }
  }

  // Build marketplace link lookup
  const linkByMarketplace: Record<string, MarketplaceLink> = {};
  for (const link of product.marketplace_links ?? []) {
    linkByMarketplace[link.marketplace] = link;
  }

  const MP_ICONS: Record<string, { icon: string; color: string; label: string }> = {
    cardmarket: { icon: "storefront", color: "#0070ba", label: "Cardmarket" },
    ebay: { icon: "pricetag", color: "#e53238", label: "eBay" },
    amazon: { icon: "cart", color: "#ff9900", label: "Amazon" },
    idealo: { icon: "search", color: "#1a5ea4", label: "Idealo" },
    geizhals: { icon: "flame", color: "#ff6600", label: "Geizhals" },
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={{ flex: 1 }}>
          <Text style={styles.tcgBadge}>
            {product.tcg.toUpperCase()}
          </Text>
          <Text style={styles.productName}>{product.name}</Text>
          <Text style={styles.setInfo}>
            {product.set_name} {product.set_code ? `(${product.set_code})` : ""}
          </Text>
          {/* Shop link icons */}
          {Object.keys(linkByMarketplace).length > 0 && (
            <View style={styles.shopIcons}>
              {(["cardmarket", "ebay", "amazon", "idealo", "geizhals"] as const).map((mp) => {
                const link = linkByMarketplace[mp];
                if (!link?.url) return null;
                const cfg = MP_ICONS[mp];
                return (
                  <TouchableOpacity
                    key={mp}
                    onPress={() => Linking.openURL(link.url)}
                    style={[styles.shopIcon, { borderColor: cfg.color }]}
                  >
                    <Ionicons name={cfg.icon as any} size={14} color={cfg.color} />
                  </TouchableOpacity>
                );
              })}
            </View>
          )}
        </View>
        <TouchableOpacity onPress={handleToggleWatchlist}>
          <Ionicons
            name={inWatchlist ? "heart" : "heart-outline"}
            size={32}
            color="#e94560"
          />
        </TouchableOpacity>
      </View>

      {/* Marketplace Prices */}
      <Text style={styles.sectionTitle}>Current Prices</Text>
      <View style={styles.pricesRow}>
        {(["cardmarket", "ebay", "amazon", "idealo", "geizhals"] as const).map((mp) => (
          <MarketplacePrice
            key={mp}
            marketplace={mp}
            price={latestByMarketplace[mp] || null}
            link={linkByMarketplace[mp] || null}
          />
        ))}
      </View>

      <TouchableOpacity
        style={styles.refreshBtn}
        onPress={handleRefresh}
        disabled={refreshing}
      >
        {refreshing ? (
          <ActivityIndicator color="#fff" size="small" />
        ) : (
          <Text style={styles.refreshBtnText}>Refresh Prices</Text>
        )}
      </TouchableOpacity>

      {/* Price History Chart */}
      {history.length > 1 && (
        <>
          <Text style={styles.sectionTitle}>Price History</Text>
          <PriceChart data={history} />
        </>
      )}

      {/* Alert Creation */}
      <Text style={styles.sectionTitle}>Set Price Alert</Text>
      <View style={styles.alertRow}>
        <TextInput
          style={styles.alertInput}
          placeholder="Target price (EUR)"
          placeholderTextColor="#666"
          keyboardType="numeric"
          value={alertPrice}
          onChangeText={setAlertPrice}
        />
        <TouchableOpacity style={styles.alertBtn} onPress={handleCreateAlert}>
          <Ionicons name="notifications" size={20} color="#fff" />
          <Text style={styles.alertBtnText}>Alert</Text>
        </TouchableOpacity>
      </View>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#16213e", padding: 16 },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#16213e",
  },
  errorText: { color: "#e94560", fontSize: 16 },
  header: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: 20,
  },
  tcgBadge: {
    color: "#e94560",
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 1,
    marginBottom: 4,
  },
  productName: {
    color: "#e0e0e0",
    fontSize: 20,
    fontWeight: "700",
    marginBottom: 4,
  },
  setInfo: { color: "#8e8e93", fontSize: 14 },
  shopIcons: {
    flexDirection: "row" as const,
    gap: 8,
    marginTop: 8,
  },
  shopIcon: {
    width: 30,
    height: 30,
    borderRadius: 15,
    borderWidth: 1.5,
    justifyContent: "center" as const,
    alignItems: "center" as const,
    backgroundColor: "#1a1a2e",
  },
  sectionTitle: {
    color: "#e0e0e0",
    fontSize: 18,
    fontWeight: "600",
    marginTop: 24,
    marginBottom: 12,
  },
  pricesRow: { gap: 10 },
  refreshBtn: {
    backgroundColor: "#0f3460",
    borderRadius: 10,
    padding: 14,
    alignItems: "center",
    marginTop: 16,
  },
  refreshBtnText: { color: "#e0e0e0", fontWeight: "600", fontSize: 15 },
  alertRow: {
    flexDirection: "row",
    gap: 10,
    alignItems: "center",
  },
  alertInput: {
    flex: 1,
    backgroundColor: "#1a1a2e",
    color: "#e0e0e0",
    borderRadius: 10,
    padding: 14,
    fontSize: 16,
    borderWidth: 1,
    borderColor: "#0f3460",
  },
  alertBtn: {
    backgroundColor: "#e94560",
    borderRadius: 10,
    padding: 14,
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  alertBtnText: { color: "#fff", fontWeight: "600" },
});
