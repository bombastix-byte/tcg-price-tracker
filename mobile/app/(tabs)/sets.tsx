import { useState, useEffect, useCallback } from "react";
import {
  View,
  FlatList,
  Text,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Image,
  ScrollView,
} from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { getSets, getTopDeals, SetSummary, BoosterValue } from "../../services/api";
import BoosterValueCard from "../../components/BoosterValueCard";

export default function SetsScreen() {
  const [sets, setSets] = useState<SetSummary[]>([]);
  const [deals, setDeals] = useState<BoosterValue[]>([]);
  const [loading, setLoading] = useState(true);
  const [tcgFilter, setTcgFilter] = useState<string | undefined>();
  const router = useRouter();

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [setsData, dealsData] = await Promise.all([
        getSets({ tcg: tcgFilter }),
        getTopDeals(10),
      ]);
      setSets(setsData);
      setDeals(dealsData);
    } catch {
      setSets([]);
      setDeals([]);
    } finally {
      setLoading(false);
    }
  }, [tcgFilter]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const renderSet = ({ item }: { item: SetSummary }) => (
    <TouchableOpacity
      style={styles.setCard}
      onPress={() => router.push(`/set/${item.set_code}`)}
      activeOpacity={0.7}
    >
      {item.logo_url ? (
        <Image
          source={{ uri: item.logo_url }}
          style={styles.logo}
          resizeMode="contain"
        />
      ) : (
        <View style={styles.logoPlaceholder}>
          <Ionicons
            name={item.tcg === "pokemon" ? "flash" : "sparkles"}
            size={28}
            color={item.tcg === "pokemon" ? "#f0a500" : "#7b68ee"}
          />
        </View>
      )}
      <View style={styles.setInfo}>
        <Text style={styles.tcgLabel}>{item.tcg.toUpperCase()}</Text>
        <Text style={styles.setName} numberOfLines={2}>
          {item.set_name}
        </Text>
        <Text style={styles.setMeta}>
          {item.release_date || "TBD"} · {item.product_count} product
          {item.product_count !== 1 ? "s" : ""}
        </Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color="#8e8e93" />
    </TouchableOpacity>
  );

  const ListHeader = () => (
    <>
      {/* TCG Filters */}
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

      {/* Top Deals Section */}
      {deals.length > 0 && (
        <View style={styles.dealsSection}>
          <Text style={styles.sectionTitle}>Top Deals</Text>
          <Text style={styles.sectionSub}>Cheapest per booster</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.dealsScroll}
          >
            {deals.map((deal, i) => (
              <BoosterValueCard key={i} item={deal} compact />
            ))}
          </ScrollView>
        </View>
      )}

      <Text style={styles.sectionTitle}>All Sets</Text>
    </>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#e94560" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={sets}
        keyExtractor={(item) => `${item.tcg}-${item.set_code}`}
        renderItem={renderSet}
        contentContainerStyle={{ paddingBottom: 20 }}
        ListHeaderComponent={ListHeader}
        ListEmptyComponent={
          <Text style={styles.empty}>No sets found.</Text>
        }
      />
    </View>
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
  filters: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 12,
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
  dealsSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    color: "#e0e0e0",
    fontSize: 18,
    fontWeight: "600",
    marginBottom: 4,
  },
  sectionSub: {
    color: "#8e8e93",
    fontSize: 12,
    marginBottom: 10,
  },
  dealsScroll: {
    marginBottom: 4,
  },
  setCard: {
    backgroundColor: "#1a1a2e",
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    flexDirection: "row",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#0f3460",
  },
  logo: {
    width: 56,
    height: 56,
    marginRight: 12,
  },
  logoPlaceholder: {
    width: 56,
    height: 56,
    borderRadius: 10,
    backgroundColor: "#16213e",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },
  setInfo: {
    flex: 1,
  },
  tcgLabel: {
    color: "#e94560",
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 1,
  },
  setName: {
    color: "#e0e0e0",
    fontSize: 15,
    fontWeight: "600",
    marginTop: 2,
  },
  setMeta: {
    color: "#8e8e93",
    fontSize: 12,
    marginTop: 2,
  },
  empty: {
    color: "#666",
    textAlign: "center",
    marginTop: 40,
    fontSize: 16,
  },
});
