import { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Image,
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { getSetDetail, SetDetail } from "../../services/api";
import ProductCard from "../../components/ProductCard";
import PriceChart from "../../components/PriceChart";
import TopCardItem from "../../components/TopCardItem";
import BoosterValueCard from "../../components/BoosterValueCard";

export default function SetDetailScreen() {
  const { code } = useLocalSearchParams<{ code: string }>();
  const [setData, setSetData] = useState<SetDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!code) return;
    (async () => {
      setLoading(true);
      setError(false);
      try {
        const data = await getSetDetail(code);
        setSetData(data);
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    })();
  }, [code]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#e94560" />
      </View>
    );
  }

  if (error || !setData) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Set not found.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        {setData.logo_url ? (
          <Image
            source={{ uri: setData.logo_url }}
            style={styles.headerLogo}
            resizeMode="contain"
          />
        ) : (
          <View style={styles.headerLogoPlaceholder}>
            <Ionicons
              name={setData.tcg === "pokemon" ? "flash" : "sparkles"}
              size={40}
              color={setData.tcg === "pokemon" ? "#f0a500" : "#7b68ee"}
            />
          </View>
        )}
        <Text style={styles.tcgBadge}>{setData.tcg.toUpperCase()}</Text>
        <Text style={styles.setName}>{setData.set_name}</Text>
        <View style={styles.metaRow}>
          {setData.release_date && (
            <View style={styles.metaChip}>
              <Ionicons name="calendar" size={12} color="#8e8e93" />
              <Text style={styles.metaChipText}>{setData.release_date}</Text>
            </View>
          )}
          <View style={styles.metaChip}>
            <Ionicons name="albums" size={12} color="#8e8e93" />
            <Text style={styles.metaChipText}>{setData.total_cards} Cards</Text>
          </View>
        </View>
      </View>

      {/* Top 5 Most Expensive Cards */}
      {setData.top_cards.length > 0 && (
        <>
          <Text style={styles.sectionTitle}>Top 5 Most Expensive Cards</Text>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.topCardsScroll}
          >
            {setData.top_cards.map((card, i) => (
              <TopCardItem key={i} card={card} rank={i + 1} />
            ))}
          </ScrollView>
        </>
      )}

      {/* Booster Value Ranking */}
      {setData.booster_values.length > 0 && (
        <>
          <Text style={styles.sectionTitle}>Booster Value Ranking</Text>
          <Text style={styles.sectionSub}>
            Sorted by price per booster · Score = top card value / display price
          </Text>
          <View style={styles.valueList}>
            {setData.booster_values.map((bv, i) => (
              <BoosterValueCard key={i} item={bv} />
            ))}
          </View>
        </>
      )}

      {/* Sealed Products */}
      <Text style={styles.sectionTitle}>
        Sealed Products ({setData.sealed_products.length})
      </Text>
      <View style={styles.productList}>
        {setData.sealed_products.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </View>

      {/* Set Price Trend */}
      {setData.price_trend.length > 1 && (
        <>
          <Text style={styles.sectionTitle}>Set Price Trend (90 Days)</Text>
          <PriceChart data={setData.price_trend} />
        </>
      )}

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
    alignItems: "center",
    marginBottom: 20,
  },
  headerLogo: {
    width: 200,
    height: 80,
    marginBottom: 12,
  },
  headerLogoPlaceholder: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: "#1a1a2e",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
  },
  tcgBadge: {
    color: "#e94560",
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 1,
    marginBottom: 4,
  },
  setName: {
    color: "#e0e0e0",
    fontSize: 22,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 8,
  },
  metaRow: {
    flexDirection: "row",
    gap: 10,
  },
  metaChip: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    backgroundColor: "#1a1a2e",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 12,
  },
  metaChipText: {
    color: "#8e8e93",
    fontSize: 12,
  },
  sectionTitle: {
    color: "#e0e0e0",
    fontSize: 18,
    fontWeight: "600",
    marginTop: 24,
    marginBottom: 4,
  },
  sectionSub: {
    color: "#8e8e93",
    fontSize: 12,
    marginBottom: 10,
  },
  topCardsScroll: {
    marginTop: 8,
    marginBottom: 4,
  },
  valueList: {
    gap: 10,
  },
  productList: {
    marginTop: 8,
  },
});
