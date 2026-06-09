import { useState, useEffect, useCallback } from "react";
import {
  View,
  TextInput,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  Text,
} from "react-native";
import { getProducts, Product } from "../../services/api";
import ProductCard from "../../components/ProductCard";

export default function SearchScreen() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [tcgFilter, setTcgFilter] = useState<string | undefined>();

  const loadProducts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getProducts({
        search: query || undefined,
        tcg: tcgFilter,
      });
      setProducts(data);
    } catch {
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, [query, tcgFilter]);

  useEffect(() => {
    const timer = setTimeout(loadProducts, 300);
    return () => clearTimeout(timer);
  }, [loadProducts]);

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.searchInput}
        placeholder="Search sealed products..."
        placeholderTextColor="#666"
        value={query}
        onChangeText={setQuery}
      />
      <View style={styles.filters}>
        {["All", "Pokemon", "Magic"].map((label) => {
          const value = label === "All" ? undefined : label.toLowerCase();
          const active = tcgFilter === value;
          return (
            <Text
              key={label}
              style={[styles.filterChip, active && styles.filterActive]}
              onPress={() => setTcgFilter(value)}
            >
              {label}
            </Text>
          );
        })}
      </View>
      {loading ? (
        <ActivityIndicator size="large" color="#e94560" style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={products}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => <ProductCard product={item} />}
          contentContainerStyle={{ paddingBottom: 20 }}
          ListEmptyComponent={
            <Text style={styles.empty}>No products found.</Text>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#16213e", padding: 16 },
  searchInput: {
    backgroundColor: "#1a1a2e",
    color: "#e0e0e0",
    borderRadius: 12,
    padding: 14,
    fontSize: 16,
    borderWidth: 1,
    borderColor: "#0f3460",
  },
  filters: {
    flexDirection: "row",
    gap: 8,
    marginVertical: 12,
  },
  filterChip: {
    color: "#8e8e93",
    backgroundColor: "#1a1a2e",
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    overflow: "hidden",
    fontSize: 14,
  },
  filterActive: {
    backgroundColor: "#e94560",
    color: "#fff",
  },
  empty: {
    color: "#666",
    textAlign: "center",
    marginTop: 40,
    fontSize: 16,
  },
});
