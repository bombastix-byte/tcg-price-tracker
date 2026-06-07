import { useState, useEffect, useCallback } from "react";
import {
  View,
  FlatList,
  StyleSheet,
  Text,
  ActivityIndicator,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useFocusEffect } from "expo-router";
import { getProduct, Product } from "../../services/api";
import ProductCard from "../../components/ProductCard";

const WATCHLIST_KEY = "tcg_watchlist";

export async function getWatchlist(): Promise<number[]> {
  const raw = await AsyncStorage.getItem(WATCHLIST_KEY);
  return raw ? JSON.parse(raw) : [];
}

export async function toggleWatchlist(productId: number): Promise<boolean> {
  const list = await getWatchlist();
  const idx = list.indexOf(productId);
  if (idx >= 0) {
    list.splice(idx, 1);
    await AsyncStorage.setItem(WATCHLIST_KEY, JSON.stringify(list));
    return false;
  }
  list.push(productId);
  await AsyncStorage.setItem(WATCHLIST_KEY, JSON.stringify(list));
  return true;
}

export default function WatchlistScreen() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const loadWatchlist = useCallback(async () => {
    setLoading(true);
    try {
      const ids = await getWatchlist();
      const results = await Promise.all(ids.map((id) => getProduct(id).catch(() => null)));
      setProducts(results.filter((p): p is Product => p !== null));
    } catch {
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadWatchlist();
    }, [loadWatchlist])
  );

  return (
    <View style={styles.container}>
      {loading ? (
        <ActivityIndicator size="large" color="#e94560" style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={products}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => <ProductCard product={item} />}
          contentContainerStyle={{ paddingBottom: 20 }}
          ListEmptyComponent={
            <Text style={styles.empty}>
              Your watchlist is empty.{"\n"}Tap the heart on a product to add it.
            </Text>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#16213e", padding: 16 },
  empty: {
    color: "#666",
    textAlign: "center",
    marginTop: 60,
    fontSize: 16,
    lineHeight: 24,
  },
});
